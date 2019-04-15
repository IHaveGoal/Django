# conding=utf-8
from flask import Flask,make_response

app = Flask(__name__)

@app.route('/')
def index():
    response = make_response('<h1>Set cookie</h1>')
    response.set_cookie('anser','44')
    return response

if __name__ == '__main__':
    app.run(debug=True)