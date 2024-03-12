#cengden server.py dosyası

from flask import Flask

app = Flask(__name__)

# Define your routes and other Flask configurations here

if __name__ == "__main__":
    print("Server is running")
    app.run()