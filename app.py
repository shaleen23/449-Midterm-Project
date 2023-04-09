from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
import pymysql
from flask_cors import CORS
import re
import jwt
import os
from datetime import timedelta
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 
# CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.config["DEBUG"] = True
app.secret_key = 'happykey'
app.permanent_session_lifetime = timedelta(minutes = 10) #added the 10 minute session expiry time 

# app.config['MYSQL_HOST'] = '127.0.0.1'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '1234'
# app.config['MYSQL_DB'] = 'test'
# To connect MySQL database
conn = pymysql.connect(
        host='localhost',
        user='root', 
        password = "shaleen23",
        db='449_db',
		cursorclass=pymysql.cursors.DictCursor
        )
cur = conn.cursor()


@app.errorhandler(400)
def page_not_found(e):
	return render_template('400.html'), 400

@app.errorhandler(401)
def unauthorized(e):
	return render_template('401.html'), 401




@app.route('/')
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		#session.permanent = True #set the permanant session to true
		cur.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
		conn.commit()
		account = cur.fetchone()
		if account:
            
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			msg = 'Logged in successfully !'
			return render_template('index.html', msg = msg)
		else: 
			#if 'loggedin' in session: #used to logout after 10 minute session
				#return redirect(url_for('index'))
			msg = 'Incorrect username / password !'
	return render_template('login.html', msg = msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'city' in request.form and 'country' in request.form and 'postalcode' in request.form and 'organisation' in request.form:
		print('reached')
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		organisation = request.form['organisation']
		address = request.form['address']
		city = request.form['city']
		state = request.form['state']
		country = request.form['country']
		postalcode = request.form['postalcode']
		cur.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cur.fetchone()
		print(account)
		conn.commit()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'name must contain only characters and numbers !'
		else:
			cur.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s, % s, % s, % s, % s, % s, % s)', (username, password, email, organisation, address, city, state, country, postalcode, ))
			conn.commit()

			msg = 'You have successfully registered !'
	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('register.html', msg = msg)


@app.route("/index")
def index():
	if 'loggedin' in session:
		return render_template("index.html")
	return redirect(url_for('login'))


@app.route("/display")
def display():
	if 'loggedin' in session:
		cur.execute('SELECT * FROM accounts WHERE id = % s', (session['id'], ))
		account = cur.fetchone()
		return render_template("display.html", account = account)
	return redirect(url_for('login'))

@app.route("/update", methods =['GET', 'POST'])
def update():
	msg = ''
	if 'loggedin' in session:
		if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form and 'address' in request.form and 'city' in request.form and 'country' in request.form and 'postalcode' in request.form and 'organisation' in request.form:
			username = request.form['username']
			password = request.form['password']
			email = request.form['email']
			organisation = request.form['organisation']
			address = request.form['address']
			city = request.form['city']
			state = request.form['state']
			country = request.form['country']
			postalcode = request.form['postalcode']
			cur.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
			account = cur.fetchone()
			if account:
				msg = 'Account already exists !'
			elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
				msg = 'Invalid email address !'
			elif not re.match(r'[A-Za-z0-9]+', username):
				msg = 'name must contain only characters and numbers !'
			else:
				cur.execute('UPDATE accounts SET username =% s, password =% s, email =% s, organisation =% s, address =% s, city =% s, state =% s, country =% s, postalcode =% s WHERE id =% s', (username, password, email, organisation, address, city, state, country, postalcode, (session['id'], ), ))
				conn.commit()
				msg = 'You have successfully updated !'
		elif request.method == 'POST':
			msg = 'Please fill out the form !'
		return render_template("update.html", msg = msg)
	return redirect(url_for('login'))

@app.route("/admin", methods =['GET', 'POST'])
def admin():
	if 'loggedin' in session and session['username'] == 'admin':
		return render_template("admin.html")

	else:
		abort(401)


@app.route('/upload')
def upload_file():
   # Make sure they are logged in before accessing the upload page
   if 'loggedin' in session:
      return render_template("upload.html")
   # If not logged in, direct them to the login page
   return redirect(url_for('login'))
	

@app.route('/upload-image', methods =['GET', 'POST'])
def upload_image():
	if request.method == "POST":
		if request.files:
			print (request.cookies.get("filesize"))
			if not allowed_image_filesize(request.cookies.get("filesize")):
				print("File exceeded maximum size")
				abort(400)
			image = request.files["image"]
			filename = secure_filename(image.filename)
			if filename != "":
				file_ext = os.path.splitext(filename)[1]
				if file_ext not in app.config['ALLOWED_IMAGE_EXTENSIONS']:
					abort(400)
				image.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
				print("image saved")    #just a msg on terminal to keep track
				return redirect(request.url)
			else:
				print("image must have a filename")
				return redirect(request.url)
	return render_template('upload_image.html')

def allowed_image_filesize(filesize):
	if int(filesize) <= app.config['MAX_IMAGE_FILESIZE']:
		print("true")
		return True
	else:
		print("false")
		return False


# Protected route
@app.route('/protected')
def protected():
    token = request.headers.get('Authorization', None)
    if not token:
        return jsonify({'message': 'Missing authorization header'}), 401

    # Decode token
    try:
        token = token.split(' ')[1]
        data = jwt.decode(token, app.config['SECRET_KEY'])
    except:
        return jsonify({'message': 'Invalid token'}), 401

    return jsonify({'message': 'Protected data'})


@app.route('/uploader', methods = ['GET', 'POST'])
def upload():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename)) 
      return 'file uploaded successfully'
if __name__ == "__main__":

	app.run(host ="localhost", port = int("5000"))
