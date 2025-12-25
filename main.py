from flask import Flask


app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/login')
def login():
    return 'Login Page'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)