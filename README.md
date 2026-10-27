# Notes Management System (SQLite3)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` (Windows PowerShell: `Copy-Item .env.example .env`) and set your own values.
3. Initialize the local SQLite database:
   ```bash
   python init_db.py
   ```
4. Start the application:
   ```bash
   python app.py
   ```

## Environment variables

- `SECRET_KEY`: Flask session and password-reset token signing key. Replace the example with a long random value.
- `MAIL_USERNAME` and `MAIL_PASSWORD`: Gmail address and Google App Password used by Flask-Mail.
- `CONTACT_EMAIL`: destination for contact-form messages.
- `FLASK_DEBUG`: set to `true` only for local development; keep `false` in production.
- `MYSQL_*`: used only by the optional MySQL-to-SQLite migration script.

## Git and secrets

`.gitignore` excludes `.env`, local database files, Python cache files, virtual environments, and IDE files. Commit `.env.example`, not `.env`. Never commit passwords, app passwords, secret keys, or database files.

If credentials were previously committed or shared, rotate them (especially the Gmail App Password) and replace them in your local `.env`.

## Optional MySQL migration

Set the `MYSQL_*` values in `.env`, run `python init_db.py`, then run `python migrate_mysql_to_sqlite.py` once. The migration refuses to run if the SQLite tables already contain data. Back up your MySQL database before migration and verify the result before removing the backup.
