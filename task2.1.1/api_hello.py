# Using flask to support REST calls
from flask import Flask

# developing a flask application
app = Flask(__name__)

# just run this on terminal to display further process of the webapp
@app.route('/')
def Home():
    return 'Good Day from Hello World Home Page. To display the message just put /hello in the end of the URL, example below'

'''
Sample working for application:
http://127.0.0.1:5000/hello
'''
# router to route to display hello world message
@app.route('/hello')
def hello_world():
    return 'Hello World REST endpoint'

# running the application
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=int("5000"),debug=True)
