from flask import Flask,request,make_response,render_template
from flask_cors import CORS, cross_origin

app = Flask(__name__)
#跨域处理
CORS(app)

@app.route('/')
# @cross_origin()
def helloworld():
    return f'helloworld'

@app.route('/greet/<name>')
def greet(name):
    return f'Hello, {name}!'

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form.get('username')
    return f'Hello, {username}!'

#响应
@app.route('/custom_response')
def custom_response():
    response = make_response('This is a custom response!')
    response.headers['token'] = '123'
    return response

@app.route('/hello/<name>')
def hello(name):
    return render_template('index.html', name=name)

@app.route('/test')
# @cross_origin()
def test():
    return f'hello,11'

@app.route('/deviceInfo',methods=['POST'])
def deviceInfo():
    name = request.form.get('gridId')
    return f'Hello, {name}!'

if __name__ == '__main__':
    app.run(debug=True)