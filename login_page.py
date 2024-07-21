import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
import sqlite3

#########################################################################
## Database functions
#########################################################################

def get_db_connection():
    return sqlite3.connect('user_data.db')

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            useremail TEXT UNIQUE,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()


#########################################################################
## User functions
#########################################################################

def sign_up(first_name, last_name, email, password, confirm_password):
    conn = get_db_connection()
    cursor = conn.cursor()

    if password != confirm_password:
        return "Passwords do not match"
    
    try:
        cursor.execute('''
            INSERT INTO users (first_name, last_name, useremail, password)
            VALUES (?, ?, ?, ?)
        ''', (first_name, last_name, email, password))
        conn.commit()
        return "Sign up successful"
    except sqlite3.IntegrityError:
        return "Email already exists"
    finally:
        conn.close()

def sign_in(email, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users WHERE useremail = ? AND password = ?
    ''', (email, password))

    user = cursor.fetchone()
    conn.close()

    if user:
        return "Sign in successful"
    else:
        return "Invalid email or password"

#########################################################################
## Error Handling functions
#########################################################################

def check_email(email):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT * FROM users WHERE useremail = ?
    ''', (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return True
    else:
        return False
    
    
    
#########################################################################
## Control panel functions
#########################################################################

def clear_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        DELETE FROM users
    ''')
    conn.commit()
    conn.close()

def get_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users") 
    data = cursor.fetchall()  
    conn.close()
    return data

#########################################################################
## Flask app
#########################################################################

app = Flask(__name__)
app.secret_key = os.urandom(16)

#########################################################################
## Navigation routes
#########################################################################

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/nav_signup')
def nav_signup():
    return render_template('signup.html')

@app.route('/nav_signin')
def nav_signin():
    return render_template('signin.html')

@app.route('/nav_secret_page')
def nav_secret_page():
    return render_template('secretPage.html')

@app.route('/logout')
def logout():
    return render_template('/')

@app.route('/nav_control_panel')
def nav_control_panel():
    data = get_data()
    return render_template('controlpanel.html', data=data)
    
#########################################################################
## User request routes
#########################################################################

@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':

        # Pulling from form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email'].lower()
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Confirming email is not used
        if check_email(email):
            flash("Email already exists", "error")
            return render_template('signup.html')
        
        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template('signup.html')
        
        result = sign_up(first_name, last_name, email, password, confirm_password)

        if result == "Sign up successful":
            return render_template('secretPage.html')
        
        else:
            return render_template('signup.html')
        
    return render_template('signup.html')


@app.route('/signin', methods=['POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if check_email(email) == False:
            flash("Invalid email or password", "error")
            return render_template('signin.html')
        
        result = sign_in(email, password)

        if result == "Sign in successful":
            return redirect(url_for('nav_secret_page'))
        
        else:
            return redirect(url_for('signin'))
    return render_template('signin.html')

#########################################################################
## Control panel route
#########################################################################

@app.route('/clear_db')
def clear_db_route():
    clear_db()
    create_table()
    return render_template('controlpanel.html', data=get_data())


# Creating the table if not already created
create_table()

#########################################################################
## Running the app
#########################################################################

if __name__ == '__main__':
    create_table()
    app.run(debug=True)