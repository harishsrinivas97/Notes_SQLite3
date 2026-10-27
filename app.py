from flask import Flask, request, redirect, render_template,url_for,session,flash
import sqlite3
import os
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired,BadSignature
import re
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-only-change-me")

app.config['MAIL_SERVER'] = 'smtp.gmail.com'   # Gmail SMTP server
app.config['MAIL_PORT'] = 587                 # Mail server port
app.config['MAIL_USE_TLS'] = True             # Use TLS encryption
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME", "")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD", "")
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", app.config['MAIL_USERNAME'])

mail = Mail(app)  # Initialize Flask-Mail with app

# Token Serializer (used for generating secure reset password links)
s = URLSafeTimedSerializer(app.secret_key)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "notes.db")

conn = sqlite3.connect(DATABASE, check_same_thread=False)
conn.row_factory = sqlite3.Row

#home page
@app.route('/')
def Home():
    return render_template('home.html')

#About page
@app.route('/about')
def About():
    return render_template("about.html")

#Contact page 
@app.route('/contact')
def Contact():
    return render_template("contact.html")

#Login page
@app.route('/login')
def Login():
    return render_template("login.html")

#forgot page
@app.route('/forgot_password')
def Forgot():
    return render_template('forgot_password.html')

#Register page
@app.route('/register')
def Register():
    return render_template('register.html')

#dashboard
@app.route('/dashboard')
def Dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('Login'))

    username = session.get('username')
    user_id = session['id']

    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM note WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    notes = cursor.fetchall()
    cursor.close()

    return render_template(
        'dashboard.html',
        username=username,
        notes=notes
    )

# Logout
@app.route("/logout")
def Logout():
    session.clear()
    flash("You have logged out successfully!", "success")
    return redirect(url_for("Home"))

#register page
@app.route('/register', methods=['GET', 'POST'])
def User_info():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        cpassword = request.form['confirm_password']

        if password != cpassword:
            flash("Passwords do not match!")
            return redirect('/register')

        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",(username, email, password))
        conn.commit()
        cur.close()

        flash("Registration successful!")
        return redirect('/login')
    return render_template('register.html')


# Verify Login
@app.route('/verify', methods=['GET', 'POST'])
def Verify():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        cur = conn.cursor()
        cur.execute("SELECT id, password FROM users WHERE username = ?",(username,))
        result = cur.fetchone()
        cur.close()

        if result is None:
            flash("You are not registered! Please sign up first.", "error")
            return redirect('/login')

        if result[1] == password:
            session['username'] = username
            session['id'] = result[0]
            session['logged_in'] = True

            flash(f"Welcome, {username}! Login successful.", "success")
            return redirect(url_for('Dashboard'))

        else:
            flash("Incorrect password. Please try again.", "error")
            return redirect('/login')

    return redirect('/login')


# Send Reset Password Email Link
@app.route('/send_reset_link', methods=['POST'])
def send_reset_link():
    email = request.form['email']

    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    cur.close()

    if user is None:
        flash("Email not registered!")
        return redirect(url_for('Forgot'))

    token = s.dumps(email, salt='password-reset-salt')

    link = url_for('reset_password', token=token, _external=True)

    msg = Message(
        "Password Reset Request",
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )

    msg.body = f"Click this link to reset your password: {link}"
    
    try:
        mail.send(msg)
        print("Email sent successfully!")
        flash("Reset link sent! Check your email inbox.", "success")
        return redirect(url_for('Login'))

    except Exception as e:
        print("Email error:", e)
        return f"Email sending failed: {e}", 500


# Reset Password Page
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(
            token,
            salt='password-reset-salt',
            max_age=300
        )
    except SignatureExpired:
        return "Link expired! Please request a new one."
    except BadSignature:
        return "Invalid reset link!"

    if request.method == 'POST':
        new_password = request.form['password']

        cur = conn.cursor()
        cur.execute(
            "UPDATE users SET password = ? WHERE email = ?",
            (new_password, email)
        )
        conn.commit()
        cur.close()

        flash("Password reset successful! Please log in.")
        return redirect(url_for('Login'))

    return render_template("reset_password.html")


# Contact Page
@app.route('/contact', methods=['GET', 'POST'])
def Contacts():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        msg = Message(
        subject="Notes Management System - Contact Form",
        sender=app.config['MAIL_USERNAME'],
        recipients=[CONTACT_EMAIL],
        reply_to=email
        )

        msg.body = f"""
        New Contact Form Submission

        Name: {name}
        Email: {email}
        Subject: {subject}

        Message:
        {message}
        """

        try:
            mail.send(msg)
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            app.logger.exception("Email sending failed")
            flash("Unable to send your message. Please try again.", "error")

        return redirect(url_for('Contact'))
    return render_template('contact.html')


# Add Note
@app.route('/addnote', methods=['GET', 'POST'])
def Addnote():
    if not session.get('logged_in'):
        return redirect(url_for('Login'))

    if request.method == 'POST':
        titel = request.form['titel']
        content = request.form['content']
        user_id = session['id']

        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO note (titel, content, user_id)
            VALUES (?, ?, ?)
            """,
            (titel, content, user_id)
        )
        conn.commit()
        cursor.close()

        flash('Note added successfully!', 'success')
        return redirect(url_for('Viewall'))

    return render_template('addnote.html')

#viewall
@app.route('/viewall')
def Viewall():
    if not session.get('logged_in'):
        return redirect(url_for('Login'))

    user_id = session['id']

    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM note WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    notes = cursor.fetchall()
    cursor.close()

    return render_template('viewall.html', notes=notes)


# View One Note
@app.route('/viewnote/<int:nid>')
def Viewnote(nid):
    if not session.get('logged_in'):
        return redirect(url_for('Login'))

    user_id = session['id']

    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM note WHERE nid = ? AND user_id = ?",
        (nid, user_id)
    )
    note = cursor.fetchone()
    cursor.close()

    if note is None:
        flash("Note not found.", "error")
        return redirect(url_for('Dashboard'))

    return render_template('viewnote.html', note=note)


# Edit Note
@app.route('/editnote/<int:nid>', methods=['GET', 'POST'])
def Editnote(nid):
    if not session.get('logged_in'):
        return redirect(url_for('Login'))

    user_id = session['id']
    cursor = conn.cursor()

    if request.method == 'POST':
        titel = request.form['titel']
        content = request.form['content']

        cursor.execute(
            """UPDATE note
               SET titel = ?, content = ?
               WHERE nid = ? AND user_id = ?""",
            (titel, content, nid, user_id)
        )
        conn.commit()
        updated = cursor.rowcount
        cursor.close()

        if updated == 0:
            # The note may not exist, belong to this user,
            # or the submitted values may be unchanged.
            flash("Note was not updated. Check that it exists.", "error")
            return redirect(url_for('Dashboard'))

        flash("Note updated successfully!", "success")
        return redirect(url_for('Dashboard'))

    cursor.execute(
        "SELECT * FROM note WHERE nid = ? AND user_id = ?",
        (nid, user_id)
    )
    note = cursor.fetchone()
    cursor.close()

    if note is None:
        flash("Note not found.", "error")
        return redirect(url_for('Dashboard'))

    return render_template('editnote.html', note=note)


# Delete Note
@app.route('/deletenote/<int:nid>', methods=['POST'])
def Deletenote(nid):
    if not session.get('logged_in'):
        return redirect(url_for('Login'))

    user_id = session['id']

    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM note WHERE nid = ? AND user_id = ?",
        (nid, user_id)
    )
    conn.commit()
    deleted = cursor.rowcount
    cursor.close()

    if deleted:
        flash("Note deleted successfully!", "success")
    else:
        flash("Note not found.", "error")

    return redirect(url_for('Dashboard'))


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")