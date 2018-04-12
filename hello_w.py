from flask import Flask

app = flask(__none__)

@app.route('/')
def hello:
    return "Hello World!"
