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

if __name__ == "__main__":
    app.secret_key = "secret_key"
    app.run(debug=True)