#cengden server.py dosyası
#MongoDB url = mongodb+srv://aavsaralpay:<password>@cluster0.khgwljs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
from flask import Flask,render_template,url_for,request,session,redirect
from flask_pymongo import PyMongo
import bcrypt


app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'aavsaralpay'
app.config['MONGO_URI'] = 'mongodb+srv://aavsaralpay:<Alpicik123.>@cluster0.khgwljs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0'
# Define your routes and other Flask configurations here

mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login',methods=['POST'])
def login():

    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'),login_user['password'].encode('utf-8')) == login_user['password'].encode('utf-8'):
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return 'Invalid username/password combination'

@app.route('/register',methods=['POST','GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if not request.form['email'].endswith('@ceng.metu.edu.tr'):
            return 'Registration is only allowed for CENG emails.'
        
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            # Store additional details
            users.insert_one({
                'email': request.form['email'],
                'password': hashpass,
                'name': request.form['name'],
                'phone': request.form['phone']
            })
            session['username'] = request.form['email']  # Consider using a more specific session key
            return redirect(url_for('index'))
        return 'That email already exists!'

    return render_template('register.html')

if __name__ == "__main__":
    app.secret_key = 'secret_key'
    app.run(debug=True)
