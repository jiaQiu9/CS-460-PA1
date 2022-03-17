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
	FOREIGN KEY (user_id) REFERENCES Registered_Users(user_id) 
		ON DELETE CASCADE
);

CREATE TABLE Photos
(
  photo_id int4 AUTO_INCREMENT PRIMARY KEY,
  user_id int4 NOT NULL,
  album_id int4 NOT NULL,
  imgdata longblob NOT NULL,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  FOREIGN KEY (user_id) REFERENCES Registered_Users(user_id) 
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
    FOREIGN KEY (user_id) REFERENCES Registered_Users(user_id) 
		ON DELETE CASCADE, 
	FOREIGN KEY (a_user_id) REFERENCES Anonymous_User(a_user_id) 
		ON DELETE CASCADE, 
	FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) 
		ON DELETE CASCADE, 
	CONSTRAINT register_or_not CHECK (
		(user_id IS NULL AND a_user_id IS NOT NULL) 
        OR 
        (user_id IS NOT NULL AND a_user_id IS NULL)
        )
	);

ALTER TABLE Comments
ADD CHECK (comments.user_id <> (SELECT user_id FROM Photos P WHERE photo_id = P.photo_id)) ;

SELECT user_id FROM Photos P WHERE photo_id = P.photo_id;

CREATE TABLE Tags(tag_name VARCHAR(50) PRIMARY KEY);

CREATE TABLE Friends_list (
	owner_id int4, 
	friend_id int4, 
    PRIMARY KEY (owner_id, friend_id), 
    FOREIGN KEY (owner_id) REFERENCES Registered_Users(user_id) 
		ON DELETE CASCADE, 
	FOREIGN KEY (friend_id) REFERENCES Registered_Users(user_id) 
		ON DELETE CASCADE
);

CREATE TABLE user_likes_photo (
	user_id  int4, 
    a_user_id int4, 
    photo_id  int4, 
    PRIMARY KEY (user_id, photo_id), 
    FOREIGN KEY (user_id) REFERENCES Registered_Users(user_id) 
		ON DELETE CASCADE, 
	FOREIGN KEY (a_user_id) REFERENCES Anonymous_User(a_user_id) 
		ON DELETE CASCADE, 
	FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) 
		ON DELETE CASCADE, 
	 CHECK (
		(user_id IS NULL AND a_user_id IS NOT NULL) 
        OR 
        (user_id IS NOT NULL AND a_user_id IS NULL)
        )
);

CREATE TABLE Photo_has_tags (
	tag_name  VARCHAR(50), 
    photo_id  int4, 
    PRIMARY KEY (tag_name, photo_id),
    FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) 
		ON DELETE CASCADE, 
	FOREIGN KEY (tag_name) REFERENCES tags(tag_name) 
		ON DELETE CASCADE); 

INSERT INTO Registered_Users (email, passcode) VALUES ('test@bu.edu', 'test');
INSERT INTO Registered_Users (email, passcode) VALUES ('test1@bu.edu', 'test');
