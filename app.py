# Store this code in 'app.py' file
from flask import Flask, render_template, request, redirect, url_for, session, abort, jsonify
# from  flask_mysqldb import MySQL
import pymysql
from flask_cors import CORS
from datetime import timedelta
import jwt
import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename

# # import MySQLdb.cursors
import re


app = Flask(__name__)

app.permanent_session_lifetime=timedelta(minutes=10)
# CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

app.secret_key = 'happykey'
os.makedirs(os.path.join(app.instance_path, 'uploads'), exist_ok=True)
app.config["IMAGE_UPLOADS"] = '../uploads' 
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"] 
app.config["MAX_IMAGE_FILESIZE"] = 5 * 1024 * 1024 

# app.config['MYSQL_HOST'] = '127.0.0.1'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '1234'
# app.config['MYSQL_DB'] = 'test'
    # To connect MySQL database

#from myproject
conn = pymysql.connect(
        host='localhost',
        user='root', 
        password = "shaleen23",
        db='449_db',
        )

cur = conn.cursor(cursor=pymysql.cursors.DictCursor)


#from myproject
@app.errorhandler(401)
def unauthorized(e):
	return jsonify(error=str(e)), 401 	

@app.errorhandler(404)
def page_not_found(e):
	return jsonify(error=str(e)), 404 	
@app.errorhandler(500)
def unexpected(e):
	return jsonify(error=str(e)), 500 	

@app.errorhandler(400)
def invalid(e):
	return jsonify(error=str(e)), 400 


#from myproject
@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow()+ datetime.timedelta(minutes=30)}, app.secret_key , algorithm="HS256")
		cur.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password, ))
		conn.commit()
		account = cur.fetchone()
		if account:
			session.permanent = True
			session['loggedin'] = True
			session['id'] = account['id']
			session['username'] = account['username']
			session['token'] = token
			msg = 'Logged in successfully !'
			return render_template('index.html', msg = msg, token = token)
		else:
			msg = 'Incorrect username / password !'
	else:
		if 'loggedin' in session:
			return render_template('index.html', msg = msg, token = session['token'])
	return render_template('login.html', msg = msg)

#from myproject
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

#from myproject
@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
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
		conn.commit()
		account = cur.fetchone()
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

#from myproject
@app.route("/index")
def index():
	if 'loggedin' in session:
		return render_template("index.html")
	return redirect(url_for('login'))

#from myproject
@app.route("/display")
def display():
	if 'loggedin' in session:
		cur.execute('SELECT * FROM accounts WHERE id = % s', (session['id'], ))
		account = cur.fetchone()
		return render_template("display.html", account = account,)
	return redirect(url_for('login'))

#from myproject
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
				msg = 'You have successfully updated !'
		elif request.method == 'POST':
			msg = 'Please fill out the form !'
		return render_template("update.html", msg = msg)
	return redirect(url_for('login'))

#from myproject
@app.route("/admin", methods =['GET', 'POST'])
def admin():
	if 'loggedin' in session and session['username'] == 'admin':
		return render_template("admin.html")

	else:
		abort(401)

# Defining the decorator function
def token_required(f):
	# Using the wraps decorator to maintain the function metadata
	@wraps(f)
	def decorated(*args, **kwargs):
		# Getting the token from the session
		token = session['token']
		# Printing the token for debugging purposes
		print('\n', token, '\n' )
		# Checking if the token is present
		if not token:
			# Returning a 500 error if the token is not present
			return abort(500)

		try:
			# Decoding the token using the app's secret key and HS256 algorithm
			data = jwt.decode(token, app.secret_key , algorithms=["HS256"])
		except:
			# Returning a 404 error if the token cannot be decoded
			return abort(404)

		# Calling the original function with the arguments and keyword arguments
		return f(*args, **kwargs)
	# Returning the decorated function
	return decorated


# Check if the filename has an allowed image extension
def allowed_image(filename):
	# If there is no period (.) in the filename, it is not a valid image file
	if not "." in filename:
		return False
	# Split the filename by the rightmost period to get the file extension
	ext = filename.rsplit(".", 1)[1]
	# Check if the file extension is in the list of allowed image extensions
	if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
		return True
	else:
		return False

# Check if the filesize is within the maximum allowed limit
def allowed_image_filesize(filesize):
	# Check if the filesize is less than or equal to the maximum allowed image filesize
	if int(filesize) <=  app.config["MAX_IMAGE_FILESIZE"]:
		return True
	else: 
		return False
	
@app.route('/')
@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		# If a POST request is received
		if request.files:
			# Check if files were uploaded in the request
			print("\n",request.files,"\n")
			print("\n",request.cookies.get("filesize"),"\n")
			# Check if the uploaded file is within the allowed file size
			if not allowed_image_filesize(request.cookies.get("filesize")):
				print("File exceeds maximum size")
				return redirect(request.url)
			# Get the uploaded image file from the request object
			image = request.files['image']
			# Check if the uploaded file has a filename
			if image.filename == "":
				print("Image must have a filename")
				return redirect(request.url)
			# Check if the uploaded file has an allowed image extension
			if not allowed_image(image.filename):
				print("That image extension is not allowed")
				return redirect(request.url)
			else:
				# If the uploaded file is valid, save it to the server
				filename = secure_filename(image.filename)
				print(f"\n Filename: {filename} \n")
				print("\n BEFORE SAVE \n")
				print(app.config["IMAGE_UPLOADS"])
				# Save the file to the server
				image.save(os.path.join(app.instance_path, 'uploads', filename))
				print("\n AFTER SAVE \n")
			print(image)
			# Redirect the user to the upload page
			return redirect(request.url)
	# If a GET request is received, render the upload.html template
	return render_template('upload.html')


@app.route('/public')
def public():

	cur.execute('SELECT COUNT(id) FROM 449_db.accounts;')
	conn.commit()
	temp = cur.fetchone()
	num = temp['COUNT(id)']

	i = 1
	all_accounts = []
	for i in range(num+1):
		
		cur.execute('SELECT id, username FROM accounts WHERE id = % s', (str(i)))
		conn.commit()
		single_account = cur.fetchone()
		all_accounts.append(single_account)
	return render_template('public.html', all_accounts = all_accounts)

@app.route('/protected')
@token_required
def protected():
	return jsonify({'message': 'Only viewed by valid tokens!'})

if __name__ == "__main__":
	app.run(host ="localhost", port = int("5000"))