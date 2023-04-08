use midterm;
CREATE TABLE accounts (
  `id` INT AUTO_INCREMENT NOT NULL,
  `username` VARCHAR(50) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `first_name` VARCHAR(255) NOT NULL,
  `last_name` VARCHAR(255) NOT NULL,
  `registration_date` DATETIME NOT NULL,
  `last_login_date` DATETIME DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY (username),
  UNIQUE KEY (email)
)ENGINE=InnODB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;	