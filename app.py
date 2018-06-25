from flask import Flask, render_template, request, logging, redirect, flash, url_for, session
from flask_mysqldb import MySQL
from wtforms import Form, StringField, PasswordField, validators, TextAreaField, BooleanField
from passlib.hash import sha256_crypt

app = Flask(__name__)

# config mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'switcher12'
app.config['MYSQL_DB'] = 'one_minute_pitch'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init mysql
mysql = MySQL(app)



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


class SignUpForm(Form):
    name = StringField('Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')


@app.route('/signup', methods=['Get', 'Post'])
def signup():
    form = SignUpForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # create cursor
        cur = mysql.connection.cursor()

        #execute Query
        cur.execute("INSERT INTO users(name, email, username, password)VALUES(%s, %s, %s, %s)", (name, email, username, password))

        #commit to db
        mysql.connection.commit()

        #close connection
        cur.close()

        flash('You are now registered!Thankyou. You can log in now', 'success')
        return redirect(url_for('index')) 

    return render_template('signup.html', form=form)

#user login
@app.route('/signin', methods=['Get', 'Post'])
def signin():
    if request.method == 'POST':

        #Get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        #Create Cursor
        cur = mysql.connection.cursor()

        #Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            #Get stored hash
            data=cur.fetchone()
            password = data['password']

            #compare the passwords
            if sha256_crypt.verify(password_candidate, password):
                #passed
                session['loggged-in'] = True
                session['username'] = username

                flash ('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'invalid sign-in'
                return render_template('signin.html', error=error)
            #Close db connection
            cur.close()


        else:
            error = 'username not found'
            return render_template('signin.html', error=error)

    return render_template('signin.html')
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.secret_key='switcher12'
    app.run(debug=True)
