# conding=utf-8
from flask import Flask,request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1>Bad Request</h1>', 438


if __name__ == '__main__':
    app.run(debug=True)