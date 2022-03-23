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
from datetime import datetime
from datetime import date
#for image uploading
import os, base64

import io


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
		<head>
			<meta charset="utf-8">
			<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
			
			<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css"
			integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
			<title>See your tags</title>
		</head>

		<nav class="navbar navbar-expand-md navbar-dark bg-dark">
		<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
		</button>
		
		<div class="collapse navbar-collapse" id="navbarNav">
			<ul class="navbar-nav mr-auto">
				<li class="nav-item active">
					<a class="nav-link" href="/home">Home <span class="sr-only">(current)</span></a>
				</li>
			</ul>

			<ul class="navbar-nav">
				<li class="nav-item">
					<a class="nav-link" href="/profile">My Profile</a>
				</li>
				<li class="nav-item">
					<a class="nav-link" href="/logout">Logout</a>
				</li>
			</ul>
    	</div>
		</nav>
		<br>
				<h1>Please log in:</h1>
				<br>
				<br>
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>

		   <style>
		   body {background-color: #212121; color: White;}
		   h1 {text-align: center;}
		   form {text-align: center;}.center {margin: auto;width: 50%;padding: 10px;}
		   </style>
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
	return "<br> <br> <br> <br> <br> <br> <br> <br>\
			<h1><a href='/login'>Try again</a> </h> <br>\
			</br><a href='/register'>or make an account</a>\
			<style>\
			body {background-color: #212121; color: White;}\
		   	h1 {text-align: center;}.center {margin: auto;width: 50%;padding: 10px;}\
			"

@app.route('/logout')
def logout():
	flask_login.logout_user()
	return render_template('hello.html', score=None, message='Logged out')

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
	test = isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Registered_Users (email, passcode) VALUES ('{0}', '{1}')".format(email, password)))
		conn.commit()
		#log user in
		user = User()
		user.id = email
		flask_login.login_user(user)
		return render_template('hello.html', score=0, name=email, message='Account Created!')
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
		themes.append({})
		
		themes[i][0] = t[i][0] #photo_id
		themes[i][1] = t[i][1] #user_id
		themes[i][2] = t[i][2] #album_id
		themes[i][3] = t[i][3] #imgdata
		themes[i][4] = t[i][4] #caption

		cursor.execute("SELECT album_name FROM Albums WHERE album_id=%s",t[i][2])
		album_name=cursor.fetchall()
		themes[i][5]= album_name[0][0] #album_name
		
		cursor.execute("SELECT pht.tag_name FROM Photo_has_tags as pht, photos AS p \
						WHERE pht.photo_id=p.photo_id and p.user_id=%s and p.photo_id=%s", (uid, t[i][0]))
		themes[i][6]=cursor.fetchall()

	cursor.execute("SELECT DISTINCT album_name FROM Albums WHERE user_id=%s",uid)
	all_album_name=cursor.fetchall()
	cursor.execute("SELECT album_id, album_name FROM Albums WHERE user_id=%s",uid)
	all_albums=cursor.fetchall()
	cursor.execute("SELECT contribution from registered_users WHERE user_id=%s",uid)
	contrib=cursor.fetchall()
	return render_template('hello.html', name=flask_login.current_user.id, score=contrib, albums=all_albums, photos=themes,base64=base64)





@app.route('/photos_recommend')
@flask_login.login_required
def photos_recommend():
	cursor=conn.cursor()
	uid=getUserIdFromEmail(flask_login.current_user.id)
	tags5 = top5_prefer()
	
	if len(tags5) != 0:
		pids_by_score = {}
		for tag in tags5:
			t = tag[0]
			cursor.execute("SELECT p.photo_id FROM Photo_has_tags as pht, Photos as p \
							WHERE p.photo_id=pht.photo_id and p.user_id<>%s and tag_name=%s", (uid,t))
			photos = cursor.fetchall()
			for p in photos:
				# add photos to pids_by_score. key is photo_id, value is the recomm_score of the photo.
				if p not in pids_by_score:
					score = recomm_score(p)
					pids_by_score[p] = score
		# get pids sorted by their recomm_score
		pids = [k for k in sorted(pids_by_score, key=pids_by_score.get, reverse=True)]
		candidates = []
		for pid in pids:
			cursor.execute("SELECT p.photo_id, r.email, a.album_name, p.caption, p.imgdata \
							FROM Photos as p, Photo_has_tags as pht, Albums as a, Registered_users as r \
							WHERE p.photo_id=pht.photo_id AND p.album_id=a.album_id AND p.user_id=r.user_id AND pht.photo_id=%s", (pid))
			recommend = cursor.fetchall()[0]

			rid = recommend[0]
			cursor.execute("SELECT tag_name FROM Photo_has_tags WHERE photo_id=%s",rid)
			rtags = cursor.fetchall()[0]
			recommend = (*recommend, rtags) 

			candidates.append(recommend)
		if len(candidates) != 0:
			return render_template('photos_recommend.html', photos=candidates, message="See photo recommendations!", base64=base64)
		else:
			return render_template('photos_recommend.html', message="You need to upload more photos to enable use to recommend.")
	else:
		return render_template('photos_recommend.html', message="You need to upload more photos to enable use to recommend.")


# recomm_score of a photo to the current user
def recomm_score(pid):
	score = 0
	tags5 = top5_prefer()

	cursor=conn.cursor()
	cursor.execute("SELECT tag_name FROM Photo_has_tags WHERE photo_id=%s", pid)
	tags = cursor.fetchall()
	for t in tags:
		if t in tags5:
			score +=1
	return score

# top5 preferred tags by the current user
def top5_prefer():
	cursor=conn.cursor()
	uid=getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("SELECT DISTINCT pht.tag_name, count(pht.photo_id) FROM Photo_has_tags as pht, tags as t, Photos as p \
					WHERE t.tag_name=pht.tag_name and pht.photo_id=p.photo_id and p.user_id=%s \
					GROUP BY pht.tag_name ORDER BY count(pht.photo_id) DESC",(uid))

	return cursor.fetchall()




# see all tags that the user has
@app.route('/user_tags', methods=['GET'])
@flask_login.login_required
def personal_tags():
	cursor=conn.cursor()
	uid=getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("SELECT DISTINCT tag_name FROM Photo_has_tags as pht, Photos as p WHERE pht.photo_id=p.photo_id and user_id=%s",(uid))
	List = cursor.fetchall()

	return render_template('user_tags.html', name=flask_login.current_user.id, tags=List)


# see photos uploaded by the users that's tagged with the <tagName>
@app.route('/<variable>/private_tagged_photos', methods=['GET'])
@flask_login.login_required
def private_tagged_photos(variable):
	themes = []
	cursor=conn.cursor()
	uid=getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("SELECT p.photo_id, p.imgdata, p.caption, p.album_id \
					FROM Photo_has_tags as pht, Photos as p \
					WHERE pht.photo_id=p.photo_id and user_id=%s and tag_name=%s",(uid, variable))
	t = cursor.fetchall()

	if len(t) == 0:
		cursor.execute("SELECT p.photo_id \
						FROM Photos as p \
						WHERE p.photo_id NOT IN\
						(SELECT p.photo_id FROM Photos as p, Photo_has_tags as pht\
						WHERE pht.photo_id=p.photo_id)")
		t = cursor.fetchall()
		for i in range(len(t)):
			themes.append({})
			themes[i][0] = t[i][0] #photo_id
			#img date
			cursor.execute("SELECT imgdata FROM photos AS p WHERE p.photo_id=%s",t[i][0])
			themes[i][1]= cursor.fetchall()[0][0]
			#caption
			cursor.execute("SELECT caption FROM photos AS p WHERE p.photo_id=%s",t[i][0])
			themes[i][2]= cursor.fetchall()[0][0]
			#album_id
			cursor.execute("SELECT album_id FROM photos AS p WHERE p.photo_id=%s",t[i][0])
			themes[i][3]= cursor.fetchall()[0][0]
			#album name
			cursor.execute("SELECT album_name FROM Albums WHERE album_id=%s",themes[i][3])
			themes[i][4]= cursor.fetchall()[0][0] 

	else:
		for i in range(len(t)):
			themes.append({})
			themes[i][0] = t[i][0] #photo_id
			themes[i][1] = t[i][1] #img date
			themes[i][2] = t[i][2] #caption
			themes[i][3] = t[i][3] #album_id	
			cursor.execute("SELECT album_name FROM Albums WHERE album_id=%s",t[i][3])
			album_name=cursor.fetchall()
			themes[i][4]= album_name[0][0] #album name
	return render_template('private_tagged_photos.html', user=uid, tag=variable, result=themes, base64=base64)


# see photos uploaded by the users that's tagged with the <tagName>
@app.route('/<variable>/public_tagged_photos', methods=['GET','POST'])
def public_tagged_photos(variable):
	themes = []
	cursor=conn.cursor()

	try:
		cursor.execute("SELECT p.imgdata, p.caption, a.album_name, r.email \
						FROM Photos as p, Albums as a, Registered_users as r, Photo_has_tags as pht \
						WHERE pht.tag_name=%s and pht.photo_id=p.photo_id and \
						p.album_id=a.album_id and p.user_id=r.user_id",(variable))
		t = cursor.fetchall()
		num = len(t) - 1
		if len(t) != 0:
			for i in range(len(t)):
				themes.append({})
				themes[i][0] = t[num-i][0] #img data
				themes[i][1] = t[num-i][1] #caption
				themes[i][2] = t[num-i][2] #album_name
				themes[i][3] = t[num-i][3] #user email
			return render_template('public_tagged_photos.html', tag=variable, message="See all photos tagged {0}.".format(variable), result=themes, base64=base64)
		else:
			return render_template('public_tagged_photos.html', tag=variable, message="Results not found. Try another tag.", result=themes, base64=base64)
	except:
		return render_template('public_tagged_photos.html', tag=variable, message="Results not found. Try another tag.", result=themes, base64=base64)

# see photos uploaded by the users that's tagged with the <tagName>
@app.route('/search_tag', methods=['POST'])
def search_tag():
	#The request method is POST (page is recieving data)
	tag = flask.request.form['search']
	return public_tagged_photos(tag)



# create album 
@app.route('/album_create', methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
	if request.method == 'POST':
		cursor=conn.cursor()
		uid = getUserIdFromEmail(flask_login.current_user.id)
		date = datetime.today()
		album_name=request.form.get('album_name')
		cursor.execute("SELECT * FROM Albums WHERE album_name=%s",(album_name))
		if (cursor.rowcount == 0):
			cursor.execute("INSERT INTO Albums (user_id, creation_date,album_name) VALUES (%s,%s,%s)",(uid,date, album_name))
			conn.commit()

			cursor.execute("SELECT contribution from registered_users WHERE user_id=%s",uid)
			contrib=cursor.fetchall()

			return render_template('hello.html', name=flask_login.current_user.id, score=contrib, message=" Album create")
		else:
			return render_template('album_create.html',message="The album name is already used by someone, enter another one.")
	return render_template('album_create.html')	
	

# see all photos in one album 
@app.route('/<variable>/photo_in_album', methods=['GET','POST'])
@flask_login.login_required
def photos_in_album(variable):
	if request.method=="GET":
		themes = []
		cursor=conn.cursor()
		uid=getUserIdFromEmail(flask_login.current_user.id)

		cursor.execute("SELECT A.album_name FROM albums as A WHERE A.album_id=%s", variable)
		Al_nam = cursor.fetchall()
		cursor.execute("SELECT creation_date From Albums Where album_id=%s", variable)
		date = cursor.fetchall()

		cursor.execute("SELECT p.photo_id, p.imgdata, p.caption \
						FROM Photos as p \
						WHERE user_id=%s and p.album_id=%s",(uid, variable))
		t = cursor.fetchall()
		if len(t) != 0:
			for i in range(len(t)):
				themes.append({})
				themes[i][0] = t[i][0] #photo_id
				themes[i][1] = t[i][1] #img date
				themes[i][2] = t[i][2] #caption
			cursor.execute("SELECT * FROM Albums WHERE user_id=%s",uid)
			all_albums=cursor.fetchall()
			return render_template('photos_in_album.html', user=uid, result=themes, albums=all_albums, date=date, message="See all your photos in {0}".format(Al_nam[0][0]), base64=base64)
		else:
			return render_template('photos_in_album.html', user=uid, result=themes, date=date, message="There's no photo in {0}".format(Al_nam[0][0]), base64=base64)
	else:
		return render_template('photos_in_album.html', user=uid, result=themes, date=date, message=None, base64=base64)


@app.route("/<variable>/delete_photo", methods=['POST', 'GET'])
@flask_login.login_required
def delete_photo(variable):
	cursor=conn.cursor()
	uid=getUserIdFromEmail(flask_login.current_user.id)
	if request.method=='POST':
		if request.form['btn']=="confirm":
			cursor.execute("SELECT tag_name from photo_has_tags WHERE photo_id=%s",variable)
			try:
				tagName = str(cursor.fetchall()[0][0])
				# update tag number
				cursor.execute("UPDATE tags SET tag_num=tag_num-1 WHERE tag_name =%s",tagName)
				conn.commit()
			except: # picture is untagged
				pass

			# update contribution - because we'll delete all commends under this photo
			cursor.execute("SELECT user_id from comments WHERE photo_id=%s", variable)
			users = cursor.fetchall()
			for user in users:
				print("\nthis user's contribution should -1:", user)
				cursor.execute("UPDATE registered_users SET contribution=contribution-1 WHERE user_id=%s", user)
				conn.commit()
			# update table comments - delete all comments under this photos from the system database
			cursor.execute("DELETE FROM Comments WHERE photo_id=%s", variable)
			conn.commit()

			# update table "photos"
			cursor.execute("DELETE FROM Photos AS p WHERE p.photo_id=%s", variable)
			# update contribution of the current user
			cursor.execute("UPDATE registered_users SET contribution=contribution-1 WHERE user_id=%s", uid)
			conn.commit()

			return render_template('hello.html', message="Deletion suceeded")
			
		elif request.form['btn']=="cancel":
			return render_template('hello.html', message="Deletion canceled")

	return render_template('delete_photo.html', photo=variable, message="Welcome back")


@app.route("/<variable>/delete_album", methods=['POST', 'GET'])
@flask_login.login_required
def delete_album(variable):
	cursor=conn.cursor()
	uid=getUserIdFromEmail(flask_login.current_user.id)
	if request.method=='POST':
		if request.form['btn']=="confirm":
			cursor.execute("SELECT photo_id from photos WHERE album_id=%s",variable)
			photos = cursor.fetchall()
			for photo in photos:
				pid = photo[0]
				cursor.execute("SELECT tag_name from photo_has_tags WHERE photo_id=%s",pid)
				tagName = str(cursor.fetchall()[0][0])
				# update tag number
				cursor.execute("UPDATE tags SET tag_num=tag_num-1 WHERE tag_name =%s",tagName)
				conn.commit()

				# update contribution - because we'll delete all commends under this photo
				cursor.execute("SELECT user_id from comments WHERE photo_id=%s", pid)
				users = cursor.fetchall()
				for user in users:
					print("\nthis user's contribution should -1:", user)
					cursor.execute("UPDATE registered_users SET contribution=contribution-1 WHERE user_id=%s", user)
					conn.commit()
				# update table comments - delete all comments under this photos from the system database
				cursor.execute("DELETE FROM Comments WHERE photo_id=%s", variable)
				conn.commit()

				# update table "photos"
				cursor.execute("DELETE FROM Photos AS p WHERE p.photo_id=%s", pid)
				conn.commit()
				# update contribution of the user
				cursor.execute("UPDATE registered_users SET contribution=contribution-1 WHERE user_id=%s", uid)
		
			# update table "albums"
			cursor.execute("DELETE FROM Albums AS a WHERE a.album_id=%s", variable)
			conn.commit()
			return render_template('hello.html', message="Deletion suceeded")

		elif request.form['btn']=="cancel":
			return render_template('hello.html', message="Deletion canceled")
	return render_template('delete_album.html', album=variable, message="Welcome back")


@app.route("/manage_albums", methods=['POST', 'GET'])
@flask_login.login_required
def manage_albums():
	cursor=conn.cursor()
	uid=getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("SELECT DISTINCT album_id, album_name FROM albums WHERE user_id=%s",(uid))
	t = cursor.fetchall()
	return render_template('manage_albums.html', albums=t)


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

		cursor.execute("SELECT album_id FROM  Albums WHERE album_name=%s and user_id=%s",(album_name,uid))
		album_result=cursor.fetchall()
		if (cursor.rowcount!=0): # the input album is in the database
		
			cursor.execute('''INSERT INTO Photos (user_id, album_id,imgdata, caption) VALUES (%s, %s, %s, %s )''' ,(uid,  album_result,photo_data,  caption))
			print("\nAdd one point", uid)

			cursor.execute("select contribution from Registered_Users as R WHERE R.user_id=%s", uid)
			print("\nsee score:", cursor.fetchall())

			cursor.execute("UPDATE Registered_Users AS R SET contribution = contribution+1 WHERE R.user_id=%s", (uid))

			cursor.execute("SELECT photo_id FROM photos ORDER BY photo_id DESC LIMIT 1")
			pid=cursor.fetchall()
			return render_template('add_tags.html', photo=pid[0][0])
			# The method is GET so we return a  HTML form to upload the a photo.
		else: # album not in user's database
			return render_template('upload.html', message="You don't have this album! Please enter an album that you have.")
	else:
		return render_template('upload.html')
#end photo uploading code

# add tags to photo
@app.route("/add_tags", methods=['POST'])
def add_tags():
	uid=getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()

	cursor.execute("SELECT contribution from registered_users WHERE user_id=%s",uid)
	contrib=cursor.fetchall()

	if request.method=="POST":
		tag = request.form.get('tag')

		pid = request.form.get('pid')
		try:
			cursor.execute("INSERT INTO tags (tag_name, tag_num) VALUES('{0}', 1)".format(tag))
			conn.commit()
		except:
			sql = "UPDATE tags SET tag_num=(tag_num+1) WHERE tag_name=%s"
			cursor.execute(sql, (tag))
			conn.commit()
		try:
			sql = "INSERT INTO Photo_has_tags (tag_name, photo_id) VALUES (%s, %s)"
			cursor.execute(sql, (tag, pid))
			conn.commit()
		except:
			sql = "INSERT INTO Photo_has_tags (tag_name, photo_id) VALUES (%s, %s)"
			cursor.execute(sql, (tag, pid))
			conn.commit()

		if request.form['btn'] == 'Add another tag':
			return render_template('add_tags.html', photo=pid, message="Tag added")
		elif request.form['btn'] == 'Add and finish':
			return render_template('hello.html', score=contrib, message="Tag added")
		else:
			return render_template('hello.html', score=contrib)



@app.route("/home", methods=['GET','POST'])
def home_page():
	return render_template('home.html')


@app.route("/all_photos", methods=['GET'])
def all_photos():
	cursor = conn.cursor()
	cursor.execute("SELECT P.photo_id, R.email, A.album_name, P.imgdata, P.caption\
					FROM Photos as P, Albums as A, Registered_Users as R\
					WHERE P.album_id=A.album_id and P.user_id=R.user_id")
	t = cursor.fetchall()
	num = len(t)-1
	themes = []
	for i in range(len(t)):
		themes.append({})
		
		themes[i][0] = t[num-i][0] #photo id
		themes[i][1] = t[num-i][1] #user email
		themes[i][2] = t[num-i][2] #album name
		themes[i][3] = t[num-i][3] #img data
		themes[i][4] = t[num-i][4] #caption
		#tags
		cursor.execute("SELECT pht.tag_name FROM photo_has_tags as pht WHERE pht.photo_id=%s", themes[i][0])
		themes[i][5] = cursor.fetchall()

		#print out comments under each photo
		# cursor.execute("select c.content, r.email from comments as c, registered_users as r where c.photo_id=%s and c.user_id",t[num-i][0])
		# current_comm=cursor.fetchall()
		# if current_comm != ():
		# 	themes[i][6]=current_comm
		# else:
		# 	themes[i][6]=current_comm

		cursor.execute(
            "select c.content, r.email from comments as c, registered_users as r where c.photo_id=%s and c.user_id=r.user_id", t[num-i][0])
		current_comm = cursor.fetchall()
		cursor.execute(
			"SELECT r.email FROM user_likes_photo as ulp, registered_users as r WHERE ulp.user_id=r.user_id AND photo_id=%s", t[num-i][0])
		lst_likes = cursor.fetchall()

		themes[i][6] = current_comm
		themes[i][7] = lst_likes
		themes[i][8] = len(lst_likes)

	return render_template('all_photos.html', result = themes, base64=base64)


# all albums 
@app.route("/all_albums", methods=['GET'])
def all_albums():
	cursor = conn.cursor()
	cursor.execute("SELECT  R.email, A.album_name, A.album_id\
					FROM  Albums as A, Registered_Users as R\
					WHERE A.user_id=R.user_id")
	t = cursor.fetchall()
	if len(t)!=0:
		num = len(t)-1
		themes = []
		for i in range(len(t)):
			themes.append({})
			
			themes[i][0] = t[num-i][0] #user email
			themes[i][1] = t[num-i][1] #album name
			themes[i][2] = t[num-i][2] #album id
		return render_template('all_albums.html', result = themes, base64=base64)
	else:
		return render_template('all_albums.html', message="There are no albums in the system.",base64=base64)



# see all photos in one album 
@app.route('/<variable>/photo_in_album_u', methods=['GET','POST'])
@flask_login.login_required
def photos_in_album_u(variable):
	if request.method=="GET":
		themes = []
		cursor=conn.cursor()
	
		cursor.execute("SELECT p.photo_id, p.imgdata, p.caption \
						FROM Photos as p, albums as a \
						WHERE p.album_id=a.album_id and p.album_id=%s",( variable))
		t = cursor.fetchall()
		cursor.execute("select album_name from albums where album_id=%s",variable)
		album_name=cursor.fetchall()
		if len(t) != 0:
			for i in range(len(t)):
				themes.append({})
				themes[i][0] = t[i][0] #photo_id
				themes[i][1] = t[i][1] #img date
				themes[i][2] = t[i][2] #caption
			
			return render_template('album_has_photos.html' ,result=themes,  message="The photos for {0}".format(album_name[0][0]), base64=base64)
		else:
			return render_template('album_has_photos.html',  message="There's no photo in {0}".format(album_name[0][0]), base64=base64)
	else:
		return render_template('album_has_photos.html', message=None, base64=base64)






@app.route("/friendslist", methods=['POST','GET'])
@flask_login.login_required
def list_friends():
	uid=getUserIdFromEmail(flask_login.current_user.id)
	cursor=conn.cursor()
	cursor.execute("SELECT friend_id FROM Friends_list WHERE owner_id=%s",uid)
	friends_list=cursor.fetchall()
	if friends_list != ():
		friends_email=[]
		for i in friends_list:
			cursor.execute("select email from registered_users where user_id = %s",i[0])
			friends_username=cursor.fetchall()
			if friends_username != ():
				friends_email.append(friends_username[0])
		return render_template('friendslist.html', list=friends_email, name=flask_login.current_user.id)
	
	return render_template('friendslist.html', name=flask_login.current_user.id)


@app.route('/add_friends',methods=['POST','GET'])
@flask_login.login_required
def add_friends():
	if request.method == 'POST':
		uid=getUserIdFromEmail(flask_login.current_user.id)
		email = request.form.get('email')
		cursor=conn.cursor()
		cursor.execute("SELECT user_id FROM registered_users WHERE email=%s",email)
		friend_id=cursor.fetchall()
		if friend_id != (): #if friend_id exists in database
			if friend_id[0][0] != uid: #if the user is not adding themself
				friendid=friend_id[0][0]
				try: 
					cursor.execute('''INSERT INTO friends_list (owner_id, friend_id) VALUES (%s, %s )''',(uid, friendid))
					conn.commit()
					cursor.execute("SELECT R.email FROM Friends_list as FL, registered_users as R WHERE FL.friend_id=R.user_id and owner_id=%s",uid)
					friends_list=cursor.fetchall()
					return render_template('friendslist.html', list=friends_list, name=flask_login.current_user.id, message="Friend was successfully added.")
				except: # if the friend is already added
					cursor.execute("SELECT R.email FROM Friends_list as FL, registered_users as R WHERE FL.friend_id=R.user_id and owner_id=%s",uid)
					friends_list=cursor.fetchall()
					return render_template('friendslist.html', list=friends_list, name=flask_login.current_user.id, message="You already added this friend.")
			else:
				return render_template('add_friend.html', name=flask_login.current_user.id, message="You can't add yourself as a friend.")
		else:
			return render_template('add_friend.html', name=flask_login.current_user.id, message="The user is not in the system.")
	return render_template('add_friend.html',name=flask_login.current_user.id)


@app.route("/top_contributors", methods=['POST', 'GET'])
def top_contributors():
	cursor.execute("SELECT email from Registered_Users as R order by R.contribution desc limit 10")
	top10 = cursor.fetchall()
	if top10 != ():
		return render_template('top_contributors.html', list=top10)
	
	return render_template('top_contributors.html')


@app.route("/top_tags", methods=['POST', 'GET'])
def top_tags():
	cursor.execute("SELECT tag_name from tags order by tag_num desc limit 10")
	top10 = cursor.fetchall()
	if top10 != ():
		return render_template('top_tags.html', list=top10)
	
	return render_template('top_tags.html')

@app.route("/<variable>/top_tagged_photos", methods=['POST', 'GET'])
def top_tagged_photos(variable):
	themes = []
	cursor=conn.cursor()
	try:
		cursor.execute("SELECT p.imgdata, p.caption, a.album_name, r.email \
						FROM Photos as p, Albums as a, Registered_users as r, Photo_has_tags as pht \
						WHERE pht.tag_name=%s and pht.photo_id=p.photo_id and \
						p.album_id=a.album_id and p.user_id=r.user_id",(variable))
		t = cursor.fetchall()
		num = len(t) - 1
		if len(t) != 0:
			for i in range(len(t)):
				themes.append({})
				themes[i][0] = t[num-i][0] #img data
				themes[i][1] = t[num-i][1] #caption
				themes[i][2] = t[num-i][2] #album_name
				themes[i][3] = t[num-i][3] #user email
			return render_template('top_tagged_photos.html', tag=variable, message="See all photos tagged {0}.".format(variable), result=themes, base64=base64)
		else:
			return render_template('top_tagged_photos.html', tag=variable, message="Results not found. Try another tag.", result=themes, base64=base64)
	except:
		return render_template('top_tagged_photos.html', tag=variable, message="Results not found. Try another tag.", result=themes, base64=base64)



@app.route("/friends_recommend", methods=['POST', 'GET'])
@flask_login.login_required
def friends_recommend():
	uid=getUserIdFromEmail(flask_login.current_user.id)
	cursor.execute("SELECT friend_id from friends_list WHERE owner_id=%s", uid)
	friends = cursor.fetchall()
	# print("\nuser's friend:",friends,"\n")
	#store friends of friends in fof: 1 col for fof_id, 1 col for appear frequency
	fof = {}
	for f in friends:
		cursor.execute("SELECT friend_id from friends_list WHERE owner_id=%s", f)
		f_friends = cursor.fetchall()
		# print("\nfriends of", f,":",f_friends,"\n")
		for ff in f_friends:
			if ff not in friends:
				cursor.execute("SELECT email from registered_users WHERE user_id=%s", ff)
				email=cursor.fetchall()[0]
				if email in fof:
					fof[email] += 1
				else:
					fof[email] = 1
	themes = [k for k in sorted(fof, key=fof.get, reverse=True)]
	#only select 20 users as friend recommendations
	if len(themes)>0:
		return render_template('friends_recommend.html', message="See your friend recommendations.", recom=themes[:20])
	else:
		return render_template('friends_recommend.html', message="You need to add more friends to get recommendations!")






# display comments of the image and be able to insert comments
@app.route("/<variable>/disp_post_comt", methods=['GET', 'POST'])
@flask_login.login_required
def disp_post_comt(variable):
    cursor = conn.cursor()
    uid = getUserIdFromEmail(flask_login.current_user.id)
    cursor.execute(
        "SELECT user_id,imgdata FROM photos WHERE photo_id=%s", variable)
    photo = cursor.fetchall()

    cursor.execute("SELECT email FROM registered_users WHERE user_id=%s", uid)
    uemail = cursor.fetchall()
    return render_template("imag_comt.html", cuid=uid, owner=photo[0][0], user_i=uemail[0][0], photo_id=variable, photo=photo, message="Insert comments for this image", base64=base64)


# inserting comment to photo
@app.route('/insert_comment', methods=['GET', "POST"])
def insert_comment():
    if request.method == 'POST':
        comment_text = request.form.get('inscom')
        user_id = request.form.get('user_id')
        photo_id = request.form.get('photo_id')

        ph_owner = request.form.get('owner')

        cursor = conn.cursor()
        date_t = date.today()
        if ph_owner == user_id:
            return render_template("all_photos.html", message="you cannot comment your own photo")
        else:
            cursor.execute("INSERT INTO comments (user_id, photo_id, content, com_date) VALUES (%s,%s,%s,%s)",
                           (user_id, photo_id, comment_text, date_t))
            conn.commit()
            cursor.execute(
                'UPDATE registered_users SET contribution=contribution+1 WHERE user_id=%s', user_id)
            conn.commit()
            return render_template("home.html", message="Comment was added")



@app.route('/likes', methods=['GET', 'POST'])
def like_photo():
	if request.method == "POST":
		photo_id = request.form.get('photo_id')
		uid = getUserIdFromEmail(flask_login.current_user.id)
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM user_likes_photo WHERE user_id=%s AND photo_id=%s", (uid, int(photo_id)))
		check_likes = cursor.fetchall()
		# user cannot like a photo that they have already liked
		if len(check_likes) == 0:
			cursor.execute("INSERT INTO user_likes_photo (user_id, photo_id) VALUES (%s, %s)", (uid, int(photo_id)))
			conn.commit()
			cursor.execute('UPDATE registered_users SET contribution=contribution+1 WHERE user_id=%s', uid)
			conn.commit()
			
			return render_template("all_photos.html", message="The photo has been liked.")

		else:
			return render_template('all_photos.html', message="You have already liked this photo.")


@app.route('/search', methods=['POST', 'GET'])
def search_comments():
	if request.method == "POST":
		cursor = conn.cursor()
		comment = request.form.get('inscom')
		cursor.execute("SELECT c.content, r.email FROM comments as c, registered_users as r WHERE \
						c.user_id=r.user_id AND c.content=%s\
						GROUP BY r.user_id \
						ORDER BY COUNT(c.content) DESC ", comment)
		lst_comment = cursor.fetchall()
		if len(lst_comment) != 0:
			return render_template('search_comment.html', list_of_comments=lst_comment)
		else:
			return render_template('search_comment.html', message="No comments in the system.")
	return render_template('search_comment.html')






#default page
@app.route("/", methods=['GET'])
def hello():
	return render_template('hello.html', score=None, message='Welecome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)