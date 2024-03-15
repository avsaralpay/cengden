#cengden server.py dosyası
#MongoDB url = mongodb+srv://aavsaralpay:<password>@cluster0.khgwljs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
from flask import Flask,render_template,url_for,request,session,redirect
from flask_pymongo import PyMongo
import bcrypt
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
import string


app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['MONGO_DBNAME'] = 'cengden'
app.config['MONGO_URI'] = 'mongodb+srv://aavsaralpay:Alpicik123.@cluster0.khgwljs.mongodb.net/cengden?retryWrites=true&w=majority&appName=Cluster0'
# Define your routes and other Flask configurations here

mongo = PyMongo(app)


def send_verification_email(email_to, name,verification_code):
    message = Mail(
        from_email='aavsaralpay@gmail.com',
        to_emails=email_to,
        subject='Verify your CENGden account',
        html_content=f'<strong>Hello {name},</strong><br>Your verification code is: <strong>{verification_code}</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))

def generate_verification_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route('/verify', methods=['POST'])
def verify():
    temp_verifications = mongo.db.temp_verifications
    users = mongo.db.users

    email = request.form.get('email')
    submitted_code = request.form.get('verification_code')
    temp_user = temp_verifications.find_one({'email': email})

    if temp_user and temp_user['verification_code'] == submitted_code:
        temp_user.pop('_id', None)  
        temp_user.pop('verification_code', None)  
        users.insert_one(temp_user)
        
        temp_verifications.delete_one({'email': email})
        
        session['email'] = email 
        return redirect(url_for('index'))
    else:
        error_message = 'Invalid verification code!'
        return render_template('verify.html', error=error_message, email=email)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        users = mongo.db.users
        email = request.form.get('email')  # Use .get for safer form data access
        login_user = users.find_one({'email': email})

        if login_user and bcrypt.checkpw(request.form.get('pass').encode('utf-8'), login_user['password']):
            session['email'] = email
            return redirect(url_for('index'))
        else:
            # Use a generic error message for security reasons
            error_message = 'Invalid email or password'
            return render_template('login.html', error=error_message)
    
    # For a GET request, just show the login form
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('email', None)  # Remove user's email from session
    return redirect(url_for('index'))

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        temp_verifications = mongo.db.temp_verifications  # Temporary collection for verification codes
        existing_user = users.find_one({'email' : request.form['email']})

        if not request.form['email'].endswith('@ceng.metu.edu.tr'):
            error_message = 'Registration is only allowed for CENG emails.'
            return render_template('register.html',error=error_message)
        
        existing_user = users.find_one({'email': email})

        if existing_user is None:
            verification_code = generate_verification_code()
            # Store additional details
            email = request.form['email']
            existing_temp_user = temp_verifications.find_one({'email': email})
            if existing_temp_user:
                temp_verifications.update_one(
                    {'email': email},
                    {'$set': {'verification_code': verification_code}}
                )
            else:
                temp_verifications.insert_one({
                    'email': email,
                    'verification_code': verification_code,
                    'name': request.form['name'],
                    'phone': request.form['phone'],
                    'password': bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
                })
            send_verification_email(email, request.form['name'], verification_code)
            session['email'] = request.form['email']  # Consider using a more specific session key
            return render_template('verify.html', email=email)
        
        error_message = 'That email already exists!'
        return render_template('register.html',error=error_message)

    return render_template('register.html')

if __name__ == "__main__":
    app.secret_key = 'secret_key'
    app.run(debug=True)
