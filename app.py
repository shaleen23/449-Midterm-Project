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
#app.config['SECRET_KEY'] = 'tokenkey'


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
        )

cur = conn.cursor(cursor=pymysql.cursors.DictCursor)

def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = session['token']
		print('\n', token, '\n' )
		if not token:
			return abort(500)

		try:
			data = jwt.decode(token, app.secret_key , algorithms=["HS256"])
		except:
			return abort(404)

		return f(*args, **kwargs)
	return decorated

app.config["IMAGE_UPLOADS"] = '../uploads' # configure image upload folder to uploads
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"] # configure allowed image extensions
app.config["MAX_IMAGE_FILESIZE"] = 5 * 1024 * 1024 # configure max image file size, 0.5MB

def allowed_image(filename):
	if not "." in filename:
		return False
	ext = filename.rsplit(".", 1)[1]
	if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
		return True
	else:
		return False

def allowed_image_filesize(filesize):
	if int(filesize) <=  app.config["MAX_IMAGE_FILESIZE"]:
		return True
	else: 
		return False
	
@app.route('/')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method == 'POST':
		if request.files:
			#print(request.cookies)
			print("\n",request.files,"\n")
			print("\n",request.cookies.get("filesize"),"\n")
			if not allowed_image_filesize(request.cookies.get("filesize")):
				print("File exceeds maximum size")
				return redirect(request.url)
			image = request.files['image']
			if image.filename == "":
				print("Image must have a filename")
				return redirect(request.url)
			if not allowed_image(image.filename):
				print("That image extension is not allowed")
				return redirect(request.url)
			else:
				filename = secure_filename(image.filename)
				print(f"\n Filename: {filename} \n")
				print("\n BEFORE SAVE \n")
				print(app.config["IMAGE_UPLOADS"])
				#image.save(app.config["IMAGE_UPLOADS"])
				
				image.save(os.path.join(app.instance_path, 'uploads', filename))

				print("\n AFTER SAVE \n")
			print(image)
			
			return redirect(request.url)
	return render_template('upload.html')


@app.route('/public')
def public():

	cur.execute('SELECT COUNT(id) FROM 449_db.accounts;')
	conn.commit()
	temp = cur.fetchone()
	num = temp['COUNT(id)']
	#print(f"\n{num}\n")

	i = 1
	all_accounts = []
	for i in range(num+1):
		
		cur.execute('SELECT id, username FROM accounts WHERE id = % s', (str(i)))
		conn.commit()
		single_account = cur.fetchone()
		#print(f"\n\n{i} \n acc: {single_account}\n\n")
		all_accounts.append(single_account)
	#print(f"\n {all_accounts} \n")
	return render_template('public.html', all_accounts = all_accounts)

@app.route('/protected')
@token_required
def protected():
	return jsonify({'message': 'Only viewed by valid tokens!'})

@app.route('/login', methods =['GET', 'POST'])
def login():
	msg = ''
	if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
		username = request.form['username']
		password = request.form['password']
		token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow()+ datetime.timedelta(minutes=30)}, app.secret_key , algorithm="HS256")
		# cursor = cur.cursor(MySQLdb.cursors.DictCursor)
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
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		organisation = request.form['organisation']
		address = request.form['address']
		city = request.form['city']
		state = request.form['state']
		country = request.form['country']
		postalcode = request.form['postalcode']
		# cursor = cur.cursor(MySQLdb.cursors.DictCursor)
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
			# cur.commit()
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
		# cursor = cur.cursor(MySQLdb.cursors.DictCursor)
		cur.execute('SELECT * FROM accounts WHERE id = % s', (session['id'], ))
		account = cur.fetchone()
		return render_template("display.html", account = account,)
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
			# cursor = cur.cursor(MySQLdb.cursors.DictCursor)
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
				# cur.commit()
				msg = 'You have successfully updated !'
		elif request.method == 'POST':
			msg = 'Please fill out the form !'
		return render_template("update.html", msg = msg)
	return redirect(url_for('login'))

@app.route("/admin")
def admin():
	if session['username'] == 'admin':
		return render_template('admin.html')
	else:
		abort(401)

@app.errorhandler(401)
def custom_401(e):
	return jsonify(error=str(e)), 401 	# not a admin

@app.errorhandler(404)
def custom_404(e):
	return jsonify(error=str(e)), 404 	# token is not found

@app.errorhandler(500)
def custom_500(e):
	return jsonify(error=str(e)), 500 	# server error
										# invalid token

@app.errorhandler(400)
def custom_400(e):
	return jsonify(error=str(e)), 400 # bad request

if __name__ == "__main__":
	app.run(host ="localhost", port = int("5000"))