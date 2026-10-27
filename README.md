Notes Management System (SQLite3)
A web-based Notes Management System built using Python Flask and SQLite3. It allows users to register, log in, and manage their personal notes. The application also includes email-based password reset functionality and a contact form.
Features
- User registration and login
- Create, view, edit, and delete personal notes
- Dashboard to manage notes
- Password reset through email
- Contact form with email notifications
- SQLite database for storing users and notes
- Environment configuration using .env
- Git security using .gitignore
Technologies Used
- Python
- Flask
- SQLite3
- HTML and CSS
- Flask-Mail
- itsdangerous
- python-dotenv
Installation and Setup
1. Clone the repository
git clone <your-repository-url>
cd Notes_SQLite3


2. Create and activate a virtual environment
python -m venv myvenv
.\myvenv\Scripts\Activate.ps1


3. Install dependencies
pip install -r requirements.txt


4. Configure environment variables

Copy .env.example to .env using PowerShell:
Copy-Item .env.example .env


Update .env with your own secret key and email credentials.

5. Initialize the database
python init_db.py


6. Run the application
python app.py


Open http://127.0.0.1:5000 in your browser.
Environment Variables
- SECRET_KEY – Flask session and password-reset token security.
- FLASK_DEBUG – Enables debug mode during development.
- MAIL_USERNAME – Gmail address used to send emails.
- MAIL_PASSWORD – Google App Password for email functionality.
- CONTACT_EMAIL – Email address that receives contact form messages.
- MYSQL_* – MySQL configuration used only for optional database migration.
Git and Security
The .gitignore file excludes .env, virtual environments, Python cache files, and local database files.

Never commit passwords, secret keys, email credentials, or .env to GitHub. Commit .env.example instead. If credentials have been exposed, revoke or change them.
Optional MySQL Migration
To migrate data from MySQL to SQLite:
1. Configure the MYSQL_* variables in .env.
2. Back up your MySQL database.
3. Follow the migration script's database initialization requirements.
4. Run:
python migrate_mysql_to_sqlite.py


Verify the migrated data before removing any backups.
Future Improvements
- Secure password hashing
- Search and sorting for notes
- Improved form validation
- Automated testing
- Production deployment
License
Add a license file if you intend to distribute this project publicly.
