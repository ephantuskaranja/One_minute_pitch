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


#comments class
class CommentsForm(Form):
    comment = TextAreaField('Comment', [validators.length(min=1)])

#Add comments 
@app.route('/add_comments/<int:id>', methods=['GET', 'POST'])
def add_comments(id):
    form = CommentsForm(request.form)
    if request.method == 'POST' and form.validate():
        comment = form.comment.data
        pitch_id = id
        
        
        # create cursor
        cur = mysql.connection.cursor()

        #execute Query
        cur.execute("INSERT INTO comments(comment,pitch_id)VALUES(%s, %s)", (comment, pitch_id))

        #commit to db
        mysql.connection.commit()

        #close connection
        cur.close()

        return redirect(url_for('show_comments')) 
    return render_template('add_comments_form.html', form= form)


#Get Comments
@app.route('/show_comments', methods=['GET'])
def show_comments():
    if request.method == 'GET':

        #Create Cursor
        cur = mysql.connection.cursor()

        #Get pcomments
        result = cur.execute("SELECT * FROM comments")
        comments = cur.fetchall()
        if result > 0:
            return render_template('show_comments.html', comments = comments)
            
        else:
            msg = 'We have no comments stored'
            flash('No comments found in db', 'danger')
            return render_template('show_comments.html', msg=msg)

        #Close connection
        cur.close()


@app.route('/latest')
def latest():
    return render_template('latest.html')

#Pitches class
class PitchesForm(Form):
    pitch = StringField('Pitch', [validators.length(min=1)])
    # category_id = StringField('Category_id', [validators.length(min=1)])


#Add pitches
@app.route('/add_pitches/<int:id>', methods=['GET','Post'])
def add_pitches(id):
    form = PitchesForm(request.form)
    category_id=id
    if request.method == 'POST':
        pitch = form.pitch.data
        
        # create cursor
        cur = mysql.connection.cursor()

        #execute Query
        cur.execute('INSERT INTO pitches(name, category_id) VALUES(%s,%s)',(pitch, category_id))
        
        #commit to db]
        mysql.connection.commit()

        #close connection
        cur.close()

        return redirect(url_for('pitches')) 

    return render_template('add_pitches_form.html', form=form)




#Get Pitches
@app.route('/pitches/', methods=['GET'])
def pitches():
    if request.method == 'GET':

        #Create Cursor
        cur = mysql.connection.cursor()

        #Get pitches
        result = cur.execute("SELECT * FROM pitches")
        pitches = cur.fetchall()
        
        if result > 0:
            return render_template('show_pitches.html', pitches = pitches)
            
        else:
            msg = 'We have no pitches stored'
            flash('No pitches found in db', 'danger')
            return render_template('show_pitches.html', msg=msg)

        #Close connection
        cur.close()
        

@app.route('/filter_pitches/<int:my_id>', methods=['GET'])
def filter_pitches(my_id):
    if request.method == 'GET':
        #Create Cursor
        cur = mysql.connection.cursor()
         
        #Get pitches--
        result = cur.execute("SELECT * FROM pitches WHERE category_id=%s "% (my_id))
        
        pitches = cur.fetchall()
        
        if result > 0:
            return render_template('filter_pitches.html', pitches = pitches)
            
        else:
            msg = 'We have no pitches stored'
            flash('No pitches found in db', 'danger')
            return render_template('filter_pitches.html', msg=msg)

        #Close connection
        cur.close()



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

#Register Users
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
        return redirect(url_for('signin')) 

    return render_template('signup.html', form=form)

#Verify users(signin)
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
                return redirect(url_for('signin'))
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


#Get Categories
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




@app.route('/dashboard/<category_id>')
def category_id(category_id):
    #Create cursor
    cur=mysql.connection.cursor()

    #Get categories
    result= cur.execute("SELECT * FROM categories WHERE ")

    categories = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', categories = categories)
        
    else:
        msg = 'We have no categories stored'
        return render_template('dashboard.html', msg=msg)

    #Close connection
    cur.close()


if __name__ == '__main__':
    app.secret_key='switcher12'
    app.run(debug=True)

