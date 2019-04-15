# conding=utf-8
from flask import Flask,redirect

app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>Hellow Zrq!</h1>'

@app.route('/zrq')
def red():
    return redirect('http://www.baidu.com')

if __name__ == '__main__':
    app.run(debug=True)