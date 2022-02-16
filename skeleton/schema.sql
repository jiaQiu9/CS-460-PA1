CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Registered_Users (
    user_id int4 AUTO_INCREMENT PRIMARY KEY,
    fst_name varchar(20),
    lst_name varchar(20),
    email varchar(255) UNIQUE,
    date_of_birth date,
    hometown varchar(255),
    gender varchar(20),
    passcode varchar(20),
    contribution int
);

CREATE TABLE Anonymous_User (
	a_user_id int4 PRIMARY KEY 
);

CREATE TABLE Albums (
	album_id int4 AUTO_INCREMENT PRIMARY KEY,
	user_id int4, 
	creation_date DATE, 
	FOREIGN KEY (user_id) REFERENCES Registered_User(user_id) 
		ON DELETE CASCADE
);

CREATE TABLE Photos
(
  photo_id int4 AUTO_INCREMENT PRIMARY KEY,
  user_id int4,
  album_id int4,
  imgdata longblob,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  FOREIGN KEY (user_id) REFERENCES Registered_User(user_id) 
	ON DELETE CASCADE, 
  FOREIGN KEY (album_id) REFERENCES albums(album_id) 
	ON DELETE CASCADE 
);

CREATE TABLE Comments ( 
	com_id int4 AUTO_INCREMENT PRIMARY KEY, 
    user_id int4, 
    a_user_id int4, 
    photo_id int4, 
    content VARCHAR(255),
    com_date DATE, 
    FOREIGN KEY (user_id) REFERENCES Registered_User(user_id) 
		ON DELETE CASCADE, 
	FOREIGN KEY (a_user_id) REFERENCES Anonymous_User(a_user_id) 
		ON DELETE CASCADE, 
	FOREIGN KEY (photo_id) REFERENCES Photo(photo_id) 
		ON DELETE CASCADE, 
	CONSTRAINT register_or_not CHECK (
		(user_id IS NULL AND a_user_id IS NOT NULL) 
        OR 
        (user_id IS NOT NULL AND a_user_id IS NULL)
        ), 
	CHECK (user_id <> (SELECT user_id FROM Photo P WHERE photo_id = P.photo_id)) 
	);

CREATE TABLE Tags(tag_name VARCHAR(50) PRIMARY KEY);


INSERT INTO Registered_Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Registered_Users (email, password) VALUES ('test1@bu.edu', 'test');
