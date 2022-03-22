# CS-460-PA1 
<b>(PhotoShare: An on-line photo social network systemPhotoShare: An on-line photo social network system)</b>

<b>Purpose of the project</b> <br>
In this project, you will design, implement and document a database system for a web-based photo sharing application. You also need to provide the web-based interface to the database. The final system should be functional and will be similar to Flickr!


Before running skeleton, turn on mysql server by type the command in terminal.

(For mac)

	To start: 'sudo /usr/local/mysql/support-files/mysql.server start' or 'brew services start mysql' (if installed from Homebrew)

	To stop:  'sudo /usr/local/mysql/support-files/mysql.server stop' or 'brew services stop mysql'

	To restart:  'sudo /usr/local/mysql/support-files/mysql.server restart' or 'brew services restart mysql'

(windows)

	To start: 'mysqld' or  'net start MySQL80' MySQL80 is the registered  service name (you can find it in services panel)
	
	To stop: 'mysqladmin -u root -p shutdown'
	
	Can also control this by MySQL Notifier

To get the skeleton running, open a terminal and do the following:

	1. enter the skeleton folder 'cd path/to/skeleton'
	
	2. install all necessary packages 'pip install -r requirements.txt' (or use pip3)
	
	3. export flask (Mac, Linux)'export FLASK_APP=app.py', (Windows)'set FLASK_APP=app.py'
	
	4. run schema.sql using MySQL Workbench
	
	5. open app.py using your favorite editor, change 'cs460' in 'app.config['MYSQL_DATABASE_PASSWORD'] = 'cs460'' to your MySQL root password. You need to keep the quotations around your root password
	
	6. back to the terminal, run the app 'python -m flask run' (or use python3)
	
	7. open your browser, and open the local website 'localhost:5000'
	
