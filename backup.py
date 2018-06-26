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



@app.route('/dashboard')
def index():
    #Create cursor
    cur=mysql.connection.cursor()

    #Get categories
    result= cur.execute("SELECT * FROM categories")

    categories = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', categories = categories)
        
    else:
        msg = 'We have no categories stored'
        return render_template('dashboard.html', msg=msg)

    #Close connection
    cur.close()



@app.route('/latest')
def latest():
    return render_template('latest.html')



@app.route('/pitches')
def pitches():
    return render_template('add_pitches_form.html')


#user signin
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
                session['signed-in'] = True
                session['username'] = username

                flash ('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'invalid sign-in'
                flash('wrong credentials', 'danger')
                return render_template('signin.html', error=error)
            #Close db connection
            cur.close()


        else:
            error = 'username not found'
            return render_template('signin.html', error=error)

    return render_template('signin.html')
    


@app.route('/signout')
def signout():
    session.clear()
    flash('You have logged out now', 'success')
    return redirect(url_for('signin'))


#category Form class
class CategoryForm(Form):
    name = StringField('Name', [validators.length(min=1)])


#add category
@app.route('/add_categories', methods=['GET', 'POST'])
def add_categories():
    form= CategoryForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data

        # Create cursor
        cur = mysql.connection.cursor()

        #Execute
        cur.execute("INSERT INTO categories(name) VALUES(%s)",[name])

        #Commit to db
        mysql.connection.commit()

        #close db connection
        cur.close()

        flash('categories added to db', 'success')

        return redirect(url_for('add_categories'))
    return render_template('add_categories_form.html', form=form)


if __name__ == '__main__':
    app.secret_key='switcher12'
    app.run(debug=True)

