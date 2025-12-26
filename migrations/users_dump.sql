PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
	id INTEGER NOT NULL, 
	username VARCHAR(20) NOT NULL, 
	nickname VARCHAR(50) NOT NULL, 
	age INTEGER NOT NULL, 
	parent_email VARCHAR(120) NOT NULL, 
	avatar_url VARCHAR(200), 
	password_hash VARCHAR(255) NOT NULL, 
	is_verified BOOLEAN, 
	verification_token VARCHAR(100), 
	created_at DATETIME, 
	last_login DATETIME, 
	color_preference VARCHAR(20), 
	privacy_settings JSON, role VARCHAR(20) DEFAULT 'student', birth_date DATE, gender VARCHAR(10), contact_phone VARCHAR(20), mailing_address TEXT, image_token_remaining INTEGER DEFAULT 50, is_enrolled BOOLEAN DEFAULT 0, daily_token_amount INTEGER DEFAULT 0, trial_end_date DATETIME, last_token_grant_date DATE, course_type VARCHAR(50), 
	PRIMARY KEY (id), 
	UNIQUE (verification_token)
);
INSERT INTO users VALUES(1,'why','王老师',12,'parent@example.com','default_avatar.png','scrypt:32768:8:1$lNj5m23IAmGunhF2$352999d0c93933329dc730e060f4708cca33e6ca57fde0f70eab29bbade1554b0b597b0e7f3dc84854a955b3e1f84368a3d1f982e102578e1f5ddac9f4fd0885',1,'c0292324-f29a-4f8b-ac4d-4249c31311e8','2025-10-25 05:57:30.953013','2025-12-23 08:03:05.537040','vibrant','{"show_in_gallery": true, "allow_sharing": true, "parental_controls": true}','teacher','1985-04-06','male','18513504311','天津市西青区精武镇万科西庐文韵园6#701',50,0,0,NULL,NULL,NULL);
COMMIT;
