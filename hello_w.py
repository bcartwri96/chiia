from flask import Flask

app = flask(__name__)

@app.route('/')
def hello_w:
    return "Hello World!"
