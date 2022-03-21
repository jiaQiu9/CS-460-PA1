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

from tkinter import Variable
from unittest import result
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask_login
import datetime
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
		fst_name=request.form.get('fst_name')
		lst_name=request.form.get('lst_name')
		email=request.form.get('email')
		date_of_birth=request.form.get('date_of_birth')
		hometown=request.form.get('hometown')
		gender=request.form.get('gender')
		password=request.form.get('password')

	except:
		print("couldn't find all tokens") #this prints to shell, end users will not see this (all print statements go to shell)
		return flask.redirect(flask.url_for('register'))
	cursor = conn.cursor()
	test = isEmailUnique(email)
	if test:
		print(cursor.execute("INSERT INTO Registered_Users (fst_name, lst_name, email, date_of_birth, hometown, gender,passcode, contribution) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}' ,'{5}', '{6}' , 0)"\
			.format(fst_name, lst_name, email, date_of_birth, hometown, gender, password)))
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

	cursor.execute("SELECT album_id, album_name FROM Albums WHERE user_id=%s",uid)
	all_albums=cursor.fetchall()
	#print("\nnumber of albums:", len(all_albums), "\n")

	return render_template('hello.html', name=flask_login.current_user.id, albums=all_albums, photos=themes,base64=base64)




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
	try:
		cursor.execute("SELECT p.photo_id, p.imgdata, p.caption, p.album_id FROM Photo_has_tags as pht, Photos as p WHERE pht.photo_id=p.photo_id and user_id=%s and tag_name=%s",(uid, variable))
	except:
		print("\nwannna see progress")
		cursor.execute("SELECT p.photo_id, p.imgdata, p.caption, p.album_id \
						FROM Photos as p \
						MINUS\
						SELECT p.photo_id, p.imgdata, p.caption, p.album_id \
						FROM Photo_has_tags as pht, Photos as p \
						WHERE pht.photo_id=p.photo_id")

	t = cursor.fetchall()
	if len(t) != 0:
		for i in range(len(t)):
			#print("album name")
			themes.append({})
			themes[i][0] = t[i][0] #photo_id
			themes[i][1] = t[i][1] #img date
			themes[i][2] = t[i][2] #caption
			themes[i][3] = t[i][3] #album_id
		
		cursor.execute("SELECT album_name FROM Albums WHERE album_id=%s",t[i][3])
		album_name=cursor.fetchall()
		themes[i][4]= album_name[0][0] #album name
		return render_template('private_tagged_photos.html', user=uid, tag=variable, result=themes, base64=base64)

	else:
		return render_template('private_tagged_photos.html', user=uid, tag=variable, result=themes, base64=base64)





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
		if (cursor.rowcount == 0):
			cursor.execute("INSERT INTO Albums (user_id, creation_date,album_name) VALUES (%s,%s,%s)",(uid,date, album_name))
			conn.commit()
			return render_template('hello.html',  name=flask_login.current_user.id,message=" Album create")
		else:
			return render_template('album_create.html',message="The album name is already used, enter another one.")
	return render_template('album_create.html')	
	

# see all photos in one album 
@app.route('/<variable>/photo_in_album', methods=['GET'])
@flask_login.login_required
def photos_in_album(variable):
	themes = []
	cursor=conn.cursor()
	uid=getUserIdFromEmail(flask_login.current_user.id)

	cursor.execute("SELECT A.album_name FROM albums as A WHERE A.album_id=%s", variable)
	Al_nam = cursor.fetchall()

	cursor.execute("SELECT p.photo_id, p.imgdata, p.caption \
					FROM Photos as p \
					WHERE user_id=%s and p.album_id=%s",(uid, variable))
	t = cursor.fetchall()
	if len(t) != 0:
		for i in range(len(t)):
			#print("album name")
			themes.append({})
			themes[i][0] = t[i][0] #photo_id
			themes[i][1] = t[i][1] #img date
			themes[i][2] = t[i][2] #caption
		
			cursor.execute("SELECT * FROM Albums WHERE user_id=%s",uid)
			all_albums=cursor.fetchall()
		
		return render_template('photos_in_album.html', user=uid, result=themes, albums=all_albums, message="See all your photos in {0}".format(Al_nam[0][0]), base64=base64)

	else:
		return render_template('photos_in_album.html', user=uid, result=themes, message="There's no photo in {0}".format(Al_nam[0][0]), base64=base64)



# display comments of the image and be able to insert comments
@app.route("/<variable>/disp_post_comt",methods=['GET','POST'])
@flask_login.login_required
def disp_post_comt(variable):
	print("photo id in display post commment ", variable)
	# themes=[]
	cursor=conn.cursor()
	uid=getUserIdFromEmail(flask_login.current_user.id)
	# cursor.execute("SELECT r.email, c.content, c.com_date FROM comments as c,registered_users as r WHERE photo_id=%s and c.user_id=r.user_id",variable)
	# t=cursor.fetchall()
	cursor.execute("SELECT user_id,imgdata FROM photos WHERE photo_id=%s",variable)
	photo=cursor.fetchall()
	
	cursor.execute("SELECT email FROM registered_users WHERE user_id=%s",uid)
	uemail=cursor.fetchall()
	print("user id for display com ",uemail[0][0])
	# print("photo comments data ",t)
	print("user id for photo ", photo[0][0])
	print("current uid ",uid)
	return render_template("imag_comt.html", cuid=uid, owner=photo[0][0],user_i=uemail[0][0], photo_id=variable, photo=photo, message="Insert comments for this image", base64=base64)
	

# inserting comment to photo
@app.route('/insert_comment',methods=['GET',"POST"])
def insert_comment():

	if request.method=='POST':
		comment_text=request.form.get('inscom')
		print('inscom ', comment_text)
		user_id=request.form.get('user_id')
		print('user id in inser comment',user_id)
		photo_id=request.form.get('photo_id')
		print("photo id ",photo_id)

		ph_owner=request.form.get('owner')
		print("photo owner :",ph_owner)


		cursor = conn.cursor()
		date=datetime.date.today()
		print("photo owner ", type(ph_owner) , " ",ph_owner)
		print("current user ", type(user_id), " ", user_id )
		print("photo owner == user id ", ph_owner == user_id)
		if ph_owner == user_id:
			return render_template("home.html", message="you cannot comment your own photo")
		else:
			cursor.execute("INSERT INTO comments (user_id, photo_id, content, com_date) VALUES (%s,%s,%s,%s)", (user_id,photo_id,comment_text,date))
			conn.commit()
			cursor.execute('UPDATE registered_users SET contribution=contribution+1 WHERE user_id=%s',user_id)
			conn.commit()
			return render_template("home.html", message="Comment was added")

#linking photo
@app.route('/likes', methods=['GET','POST'])
def like_photo():
	if request.method== "POST":
		photo_id=request.form.get('photo_id')
		uid=getUserIdFromEmail(flask_login.current_user.id)
		cursor=conn.cursor()
		cursor.execute("SELECT * FROM user_likes_photo WHERE user_id=%s AND photo_id=%s", (uid, int(photo_id)) )
		check_likes=cursor.fetchall()
		print("check_likes ",check_likes)
		if len(check_likes) ==0 :
			cursor.execute("INSERT INTO user_likes_photo (user_id, photo_id) VALUES (%s, %s)",(uid, int(photo_id)))
			conn.commit()
			cursor.execute('UPDATE registered_users SET contribution=contribution+1 WHERE user_id=%s',uid)
			conn.commit()
		# need a render template
			return render_template("home.html", message="The photo has been liked.")
		else:
			return render_template('home.html',message="You have already liked this photo.")

# search comments
@app.route('/search', methods=['POST','GET'])
def search_comments():
	if request.method == "POST":
		cursor=conn.cursor()
		comment=request.form.get('inscom')
		cursor.execute("SELECT c.content, r.email FROM comments as c, registered_users as r WHERE \
			c.user_id=r.user_id AND c.content=%s\
				 GROUP BY r.user_id \
					 ORDER BY COUNT(c.content) DESC ",comment)
		lst_comment=cursor.fetchall()
		print("lst of matched comments ", lst_comment)
		return render_template('search_comment.html', list_of_comments=lst_comment)
	return render_template('search_comment.html')

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
			cursor.execute("UPDATE Registered_Users AS R SET contribution = contribution + 1 WHERE R.user_id=%s", (uid))
			conn.commit()
			cursor.execute("SELECT photo_id FROM photos ORDER BY photo_id DESC LIMIT 1")
			pid=cursor.fetchall()
			print("\nwhen we upload the file, pid is:", pid,"\n")
			return render_template('add_tags.html', photo=pid[0][0])
			# return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPhotos(uid),base64=base64)
			# The method is GET so we return a  HTML form to upload the a photo.
		else:
			return render_template('upload.html')
	else:
		return render_template('upload.html')
#end photo uploading code

# add tags to photo
@app.route("/add_tags", methods=['POST'])
def add_tags():
	uid=getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	if request.method=="POST":
		tag = request.form.get('tag')
		print("\nget tag:", tag)

		pid = request.form.get('pid')
		print("\nget pid:", pid, "\n")
		try:
			cursor.execute("INSERT INTO tags (tag_name, tag_num) VALUES('{0}', 1)".format(tag))
			conn.commit()
			print("first try")
		except:
			sql = "UPDATE tags SET tag_num=(tag_num+1) WHERE tag_name=%s"
			cursor.execute(sql, (tag))
			conn.commit()
			print("first except ")
		try:
			sql = "INSERT INTO Photo_has_tags (tag_name, photo_id) VALUES (%s, %s)"
			cursor.execute(sql, (tag, pid))
			conn.commit()
			print("2nd t")
		except:
			sql = "INSERT INTO Photo_has_tags (tag_name, photo_id) VALUES (%s, %s)"
			cursor.execute(sql, (tag, pid))
			conn.commit()
			print("2nd t")

		print("pid in post if ", pid)
		if request.form['btn'] == 'Add another tag':
			print(request.form['btn'])
			print("pid add another tag ", pid)
			return render_template('add_tags.html', photo=pid)
		elif request.form['btn'] == 'Add and finish':
			print(request.form['btn'])
			return render_template('hello.html')
		else:
			print(request.form['btn'])
			return render_template('hello.html')




@app.route("/home", methods=['GET','POST'])
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
		#print out comments under each photo
		cursor.execute("select c.content, r.email from comments as c, registered_users as r where c.photo_id=%s and c.user_id=r.user_id",t[i][0])
		current_comm=cursor.fetchall()
		print("comment user and comment ", current_comm)
		#for list of likes of each photo
		cursor.execute("SELECT r.email FROM user_likes_photo as ulp, registered_users as r WHERE ulp.user_id=r.user_id AND photo_id=%s", t[i][0])
		lst_likes=cursor.fetchall()
	
		themes[i][6]=current_comm
		
		themes[i][7]=lst_likes
		print("lst likes ",lst_likes, " ", " photo_id: ",t[i][0])
		
	return render_template('home.html', result = themes,base64=base64)





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
		print("email ",email)
		cursor=conn.cursor()
		cursor.execute("SELECT user_id FROM registered_users WHERE email=%s",email)
		friend_id=cursor.fetchall()
		if friend_id != ():
			print("friend id",friend_id[0][0])
			if friend_id[0][0] != uid:
				print("friend list ", friend_id, uid)
				friendid=friend_id[0][0]
				cursor.execute('''INSERT INTO friends_list (owner_id, friend_id) VALUES (%s, %s )''',(uid, friendid))
				conn.commit()
				return render_template('home.html', message="friend was successfully added")
		else:
			return render_template('add_friend.html',name=flask_login.current_user.id, message="The user is not in the system.")
	return render_template('add_friend.html',name=flask_login.current_user.id)


@app.route("/top_contributors", methods=['POST', 'GET'])
def show_top10():
	cursor.execute("SELECT email from Registered_Users as R order by R.contribution desc limit 10")
	top10 = cursor.fetchall()
	if top10 != ():
		return render_template('top_contributors.html', list=top10)
	
	return render_template('top_contributors.html')




#default page
@app.route("/", methods=['GET'])
def hello():

	return render_template('hello.html', message='Welecome to Photoshare')


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
