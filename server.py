#cengden server.py dosyası
#MongoDB url = mongodb+srv://aavsaralpay:<password>@cluster0.khgwljs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
from flask import Flask,render_template,url_for,request,session,redirect
from flask_pymongo import PyMongo
import bcrypt


app = Flask(__name__)
app.secret_key = 'secret_key'
app.config['MONGO_DBNAME'] = 'cengden'
app.config['MONGO_URI'] = 'mongodb+srv://aavsaralpay:Alpicik123.@cluster0.khgwljs.mongodb.net/cengden?retryWrites=true&w=majority&appName=Cluster0'
# Define your routes and other Flask configurations here

mongo = PyMongo(app)

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

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        print(request.form)  # Log the form data for debugging
        users = mongo.db.users
        existing_user = users.find_one({'email' : request.form['email']})
        if not request.form['email'].endswith('@ceng.metu.edu.tr'):
            error_message = 'Registration is only allowed for CENG emails.'
            return render_template('register.html',error=error_message)

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            # Store additional details
            try:
                users.insert_one({
                    'email': request.form['email'],
                    'password': hashpass,
                    'name': request.form['name'],
                    'phone': request.form['phone'],
                    'role': 'authenticated_user'  # Assign a default role
                })
            except Exception as e:
                print(e)
                return 'An error occurred while registering the user.'

            session['email'] = request.form['email']  # Consider using a more specific session key
            return redirect(url_for('index'))
        
        error_message = 'That email already exists!'
        return render_template('register.html',error=error_message)

    return render_template('register.html')

if __name__ == "__main__":
    app.secret_key = 'secret_key'
    app.run(debug=True)
