######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

from unittest import result
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
import datetime
#for image uploading
import os, base64

import io

from sympy import Q

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'cs460pa1'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email from Registered_Users")
users = cursor.fetchall()

def getUserList():
	cursor = conn.cursor()
	cursor.execute("SELECT email from Registered_Users")
	return cursor.fetchall()

class User(flask_login.UserMixin):
	pass

@login_manager.user_loader
def user_loader(email):
	users = getUserList()
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	users = getUserList()
	email = request.form.get('email')
	if not(email) or email not in str(users):
		return
	user = User()
	user.id = email
	cursor = mysql.connect().cursor()
	cursor.execute("SELECT password FROM Registered_Users WHERE email = '{0}'".format(email))
	data = cursor.fetchall()
	pwd = str(data[0][0] )
	user.is_authenticated = request.form['password'] == pwd
	return user

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
	if flask.request.method == 'GET':
		return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
	#The request method is POST (page is recieving data)
	email = flask.request.form['email']
	cursor = conn.cursor()
	#check if email is registered
	if cursor.execute("SELECT passcode FROM Registered_Users WHERE email = '{0}'".format(email)):
		data = cursor.fetchall()
		pwd = str(data[0][0] )
		if flask.request.form['password'] == pwd:
			user = User()
			user.id = email
			flask_login.login_user(user) #okay login in user
			return flask.redirect(flask.url_for('protected')) #protected is a function defined in this file

	#information did not match
	return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', message='Logged out')

@login_manager.unauthorized_handler
def unauthorized_handler():
	return render_template('unauth.html')

#you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
	return render_template('register.html', supress='True')

@app.route("/register", methods=['POST'])
def register_user():
	try:
		email=request.form.get('email')
		password=request.form.get('password')
	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test =  isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Registered_Users (email, passcode) VALUES ('{0}', '{1}')".format(email, password)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', name=email, message='Account Created!')
	else:
		print("couldn't find all tokens")
		return flask.redirect(flask.url_for('register'))

@app.route('/noregister')
def noregister_user():
	return render_template('noregister.html')




def getUsersPhotos(uid):
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id, user_id, album_id, imgdata,  caption FROM Photos WHERE user_id = '{0}'".format(uid))
	return cursor.fetchall() #NOTE list of tuples, [(imgdata, pid), ...]

def getUserIdFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT user_id  FROM Registered_Users WHERE email = '{0}'".format(email))
	return cursor.fetchone()[0]

def isEmailUnique(email):
	#use this to check if a email has already been registered
	cursor = conn.cursor()
	if cursor.execute("SELECT email  FROM Registered_Users WHERE email = '{0}'".format(email)):
		#this means there are greater than zero entries with that email
		return False
	else:
		return True
#end login code

@app.route('/profile')
@flask_login.login_required
def protected():
	themes=[]
	cursor=conn.cursor()
	uid=getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("SELECT photo_id, user_id, album_id, imgdata, caption FROM Photos WHERE user_id=%s ",(uid))
	t = cursor.fetchall()
	for i in range(len(t)):
		#print(t[i][2])
		themes.append({})
		
		themes[i][0] = t[i][0]
		themes[i][1] = t[i][1]
		
		themes[i][2] = t[i][2]
		themes[i][3] = t[i][3]
		themes[i][4] = t[i][4]
		#print("abum_id: ",t[i][2])
		cursor.execute("SELECT album_name FROM Albums WHERE album_id=%s",t[i][2])
		album_name=cursor.fetchall()
		#print("album_name :")
		themes[i][5]= album_name[0][0]
	cursor.execute("SELECT DISTINCT album_name FROM Albums WHERE user_id=%s",uid)
	all_album_name=cursor.fetchall()
	#print("album name of the current user",all_album_name[0][0])

	return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile",a_name=all_album_name, photos=themes,base64=base64)



# create album 
@app.route('/album_create', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
	if request.method == 'POST':
		cursor=conn.cursor()
		uid = getUserIdFromEmail(flask_login.current_user.id)
		date = datetime.date.today()
		album_name=request.form.get('album_name')
		cursor.execute("SELECT * FROM Albums WHERE album_name=%s",album_name)
		result=cursor.fetchall()
		print(cursor.rowcount)
		if (cursor.rowcount == 0 ):
			cursor.execute("INSERT INTO Albums (user_id, creation_date,album_name) VALUES (%s,%s,%s)",(uid,date, album_name))
			conn.commit()
			return render_template('hello.html',  name=flask_login.current_user.id,message=" Album create")
		else:
			return render_template('album_create.html',message="The album name is already used, enter another one.")
	return render_template('album_create.html')	
	


#begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
	if request.method == 'POST':
		uid = getUserIdFromEmail(flask_login.current_user.id)
		imgfile = request.files['photo']
		caption = request.form.get('caption')
		album_name= request.form.get('album')
		photo_data =imgfile.read()
		cursor = conn.cursor()
		cursor.execute("SELECT album_id FROM  Albums WHERE album_name=%s",(album_name))
		album_result=cursor.fetchall()
		if (cursor.rowcount!=0):
			print(uid,  album_result,  caption)
			cursor.execute('''INSERT INTO Photos (user_id, album_id,imgdata, caption) VALUES (%s, %s, %s, %s )''' ,(uid,  album_result,photo_data,  caption))
			conn.commit()
			return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid),base64=base64)
			#The method is GET so we return a  HTML form to upload the a photo.
		else:
			return render_template('upload.html')

	else:
		return render_template('upload.html')
#end photo uploading code


@app.route("/home", methods=['GET'])
def home_page():
	themes = []
	cursor = conn.cursor()
	cursor.execute("SELECT photo_id, user_id, album_id, imgdata, caption FROM Photos")
	t = cursor.fetchall()
	for i in range(len(t)):
		#print("album name")
		themes.append({})
		
		themes[i][0] = t[i][0] #photo id
		themes[i][1] = t[i][1] # user if
		themes[i][2] = t[i][2] # album_id
		themes[i][3] = t[i][3] #img date
		themes[i][4] = t[i][4] # caption
		cursor.execute("SELECT album_name FROM Albums WHERE album_id=%s",t[i][2])
		album_name=cursor.fetchall()
		#print("album_name :", album_name[0][0])
		themes[i][5]= album_name[0][0] #album name
	return render_template('home.html', result = themes,base64=base64)





@app.route("/friendslist", methods=['POST','GET'])
@flask_login.login_required
def list_friends():
	uid=getUserIdFromEmail(flask_login.current_user.id)
	cursor=conn.cursor()
	cursor.execute("SELECT friend_id FROM Friends_list WHERE owner_id=%s",uid)
	friends_list=cursor.fetchall()
	if friends_list != ():
		cursor.execute("SELECT email FROM registered_users where user_id IN %s",friends_list)
		friends_username=cursor.fetchall()
		
		if friends_list != ():
			return render_template('friendslist.html', list=friends_username, name=flask_login.current_user.id)
	
	return render_template('friendslist.html', name=flask_login.current_user.id)

@app.route('/add_friends',methods=['POST','GET'])
@flask_login.login_required
def add_friends():
	if request.method == 'POST':
		uid=getUserIdFromEmail(flask_login.current_user.id)
		email = request.form.get('email')
		print("email ",email)
		cursor=conn.cursor()
		cursor.execute("SELECT user_id FROM registered_users WHERE email=%s",email)
		friend_id=cursor.fetchall()
		if friend_id != ():
			print("friend id",friend_id[0][0])
			if friend_id[0][0] != uid:
				print("friend list ", friend_id, uid)
				cursor.execute('''INSERT INTO friends_list (owner_id, friend_id) VALUES (%s, %s )''',(uid, friend_id))
				conn.commit()
	return render_template('add_friend.html',name=flask_login.current_user.id)



#default page
@app.route("/", methods=['GET'])
def hello():

	return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
