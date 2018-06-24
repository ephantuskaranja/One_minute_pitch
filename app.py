from flask import Flask, render_template, redirect, flash, url_for, session
app = Flask(__name__)
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/pitches')
def pitches():
    return render_template('pitches.html')

@app.route('/latest')
def latest():
    return render_template('latest.html')

@app.route('/most_voted')
def mostVoted():
    return render_template('most_voted.html')
    


@app.route('/favourites')
def favourites():
    return render_template('favourites.html')
    

class RegisterForm(Form):
    name = StringField('Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

if __name__ == '__main__':
    app.run(debug=True)
