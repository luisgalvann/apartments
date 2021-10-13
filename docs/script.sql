-- Deleting DataBase
DROP SCHEMA IF EXISTS `apartment_manager_db`;

-- Creating DataBase
CREATE SCHEMA `apartment_manager_db`;

-- Creating table: 'entity'
CREATE TABLE `apartment_manager_db`.`entity` (
    `id` int unsigned AUTO_INCREMENT,

    PRIMARY KEY (`id`)
);

-- Creating table: 'document'
CREATE TABLE `apartment_manager_db`.`document` (
    `id` int unsigned AUTO_INCREMENT,
    `foreign_entity_id` int unsigned NOT NULL,
    `file_path` text NOT NULL,

    PRIMARY KEY (`id`),
    CONSTRAINT `fk_document_foreign_entity` FOREIGN KEY (`foreign_entity_id`) REFERENCES entity(`id`) ON DELETE CASCADE
);

-- Creating table: 'country'
CREATE TABLE `apartment_manager_db`.`country` ( 
    `id` int unsigned AUTO_INCREMENT,
    `country_name` varchar(50) NOT NULL,

    PRIMARY KEY (`id`)
);

-- Creating table: 'city'
CREATE TABLE `apartment_manager_db`.`city` ( 
    `id` int unsigned AUTO_INCREMENT,
    `city_name` varchar(50) NOT NULL,
    `country_id` int unsigned NOT NULL,

    PRIMARY KEY (`id`),
    CONSTRAINT `fk_city_country` FOREIGN KEY (`country_id`) REFERENCES country(`id`) ON DELETE CASCADE
);

-- Creating table: 'customer'
CREATE TABLE `apartment_manager_db`.`customer` (
    `id` int unsigned AUTO_INCREMENT,
    `entity_id` int unsigned NOT NULL UNIQUE,
    `first_name` varchar(50) NOT NULL,
    `last_name` varchar(50) NOT NULL,
    `phone` varchar(50),
    `email` varchar(50),
    `language` varchar(50),
    `country_id` int unsigned NOT NULL,
    `city_id` int unsigned NOT NULL,
    `address` varchar(100),
    `zip_code` varchar(50),
    `notes` text,

    PRIMARY KEY (`id`),
    CONSTRAINT `fk_customer_entity` FOREIGN KEY (`entity_id`) REFERENCES entity(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_customer_country` FOREIGN KEY (`country_id`) REFERENCES country(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_customer_city` FOREIGN KEY (`city_id`) REFERENCES city(`id`) ON DELETE CASCADE
);

-- Creating table: 'owner'
CREATE TABLE `apartment_manager_db`.`owner` ( 
    `id` int unsigned AUTO_INCREMENT,
    `entity_id` int unsigned NOT NULL UNIQUE,
    `first_name` varchar(50) NOT NULL,
    `last_name` varchar(50) NOT NULL,
    `phone` varchar(50),
    `email` varchar(50),
    `language` varchar(50),
    `country_id`  int unsigned NOT NULL,
    `city_id`  int unsigned NOT NULL,
    `address` varchar(100),
    `zip_code` varchar(50),
    `notes` text,

    PRIMARY KEY (`id`),
    CONSTRAINT `fk_owner_entity` FOREIGN KEY (`entity_id`) REFERENCES entity(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_owner_country` FOREIGN KEY (`country_id`) REFERENCES country(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_owner_city` FOREIGN KEY (`city_id`) REFERENCES city(`id`) ON DELETE CASCADE
);

-- Creating table: 'agency'
CREATE TABLE `apartment_manager_db`.`agency` ( 
    `id` int unsigned AUTO_INCREMENT,
    `entity_id` int unsigned NOT NULL UNIQUE,
    `agency_name` varchar(50) NOT NULL,
    `phone` varchar(50),
    `contact_person` varchar(50),
    `cp_phone` varchar(50),
    `email` varchar(50),
    `website` varchar(50),
    `country_id`  int unsigned NOT NULL,
    `city_id`  int unsigned NOT NULL,
    `address` varchar(100),
    `zip_code` varchar(50),
    `notes` text,

    PRIMARY KEY (`id`),
    CONSTRAINT `fk_agency_entity` FOREIGN KEY (`entity_id`) REFERENCES entity(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_agency_country` FOREIGN KEY (`country_id`) REFERENCES country(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_agency_city` FOREIGN KEY (`city_id`) REFERENCES city(`id`) ON DELETE CASCADE
);

-- Creating table: 'apartment'
CREATE TABLE `apartment_manager_db`.`apartment` ( 
    `id` int unsigned AUTO_INCREMENT,
    `entity_id` int unsigned NOT NULL UNIQUE,
    `apartment_name` varchar(50) NOT NULL,
    `phone` varchar(50),
    `owner_id` int unsigned NOT NULL,
    `max_guests` smallint unsigned,
    `country_id`  int unsigned NOT NULL,
    `city_id`  int unsigned NOT NULL,
    `address` varchar(100),
    `zip_code` varchar(50),
    `location` varchar(50),
    `parking_spaces` smallint unsigned,
    `elevator` boolean DEFAULT NULL,
    `notes` text,

    PRIMARY KEY (`id`),
    CONSTRAINT `fk_apartment_entity` FOREIGN KEY (`entity_id`) REFERENCES entity(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_apartment_owner` FOREIGN KEY (`owner_id`) REFERENCES owner(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_apartment_country` FOREIGN KEY (`country_id`) REFERENCES country(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_apartment_city` FOREIGN KEY (`city_id`) REFERENCES city(`id`) ON DELETE CASCADE
);

-- Creating table: 'photo'
CREATE TABLE `apartment_manager_db`.`photo` ( 
    `id` int unsigned AUTO_INCREMENT,
    `apartment_id`   int unsigned NOT NULL,
    `file_path` text NOT NULL,

    PRIMARY KEY (`id`),
    CONSTRAINT `fk_photo_apartment` FOREIGN KEY (`apartment_id`) REFERENCES apartment(`id`) ON DELETE CASCADE
);

-- Creating table: 'employee_category'
CREATE TABLE `apartment_manager_db`.`employee_category` ( 
    `id` smallint unsigned AUTO_INCREMENT,
    `category` varchar(50) NOT NULL,

    PRIMARY KEY (`id`)
);

-- Creating table: 'employee'
CREATE TABLE `apartment_manager_db`.`employee` (
    `id` int unsigned AUTO_INCREMENT,
    `entity_id` int unsigned NOT NULL UNIQUE,
    `first_name` varchar(50) NOT NULL,
    `last_name` varchar(50) NOT NULL,
    `phone` varchar(50),
    `email` varchar(50),
    `category_id` smallint unsigned NOT NULL,
    `start_date` date,
    `end_date` date,
    `country_id`  int unsigned NOT NULL,
    `city_id`  int unsigned NOT NULL,
    `address` varchar(100),
    `zip_code` varchar(50),
    `notes` text,

    PRIMARY KEY (`id`),
    CONSTRAINT `fk_employee_entity` FOREIGN KEY (`entity_id`) REFERENCES entity(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_employee_category` FOREIGN KEY (`category_id`) REFERENCES employee_category(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_employee_country` FOREIGN KEY (`country_id`) REFERENCES country(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_employee_city` FOREIGN KEY (`city_id`) REFERENCES city(`id`) ON DELETE CASCADE
);

-- Creating table: 'reservation'
CREATE TABLE `apartment_manager_db`.`reservation` ( 
    `id` int unsigned AUTO_INCREMENT,
    `entity_id` int unsigned NOT NULL UNIQUE,
    `customer_id` int unsigned NOT NULL,
    `agency_id` int unsigned NOT NULL,
    `apartment_id` int unsigned NOT NULL,
    `checkin_date` date NOT NULL,
    `checkout_date` date NOT NULL,
    `guests` smallint unsigned,
    `amount` float(10) unsigned,
    `tax` float(10) unsigned,
    `caution` float(10) unsigned,
    `notes` TEXT,

    PRIMARY KEY (`id`),
    CONSTRAINT `fk_reservation_entity` FOREIGN KEY (`entity_id`) REFERENCES entity(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reservation_customer` FOREIGN KEY (`customer_id`) REFERENCES customer(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reservation_agency` FOREIGN KEY (`agency_id`) REFERENCES agency(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_reservation_apartment` FOREIGN KEY (`apartment_id`) REFERENCES apartment(`id`) ON DELETE CASCADE
);

-- Creating table: 'service_type'
CREATE TABLE `apartment_manager_db`.`service_type` ( 
    `id` smallint unsigned AUTO_INCREMENT,
    `type` varchar(50) NOT NULL,

    PRIMARY KEY (`id`)
);

-- Creating table: 'service_category'
CREATE TABLE `apartment_manager_db`.`service_category` ( 
    `id` smallint unsigned AUTO_INCREMENT,
    `category` varchar(50) NOT NULL,

    PRIMARY KEY (`id`)
);

-- Creating table: 'service'
CREATE TABLE `apartment_manager_db`.`service` ( 
    `id` int unsigned AUTO_INCREMENT,
    `reservation_id` int unsigned NOT NULL,
    `category_id` smallint unsigned NOT NULL,
    `type_id` smallint unsigned NOT NULL,
    `employee_id` int unsigned NOT NULL,
    `date` date,
    `time` time,
    `hours` time,
    `extra_price` float(10),
    `notes` text,

    PRIMARY KEY (`id`),
    CONSTRAINT `fk_service_reservation` FOREIGN KEY (`reservation_id`) REFERENCES reservation(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_service_service_category` FOREIGN KEY (`category_id`) REFERENCES service_category(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_service_service_type` FOREIGN KEY (`type_id`) REFERENCES service_type(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_service_employee` FOREIGN KEY (`employee_id`) REFERENCES employee(`id`) ON DELETE CASCADE
);

-- Creating table: 'user_permission'
CREATE TABLE `apartment_manager_db`.`user_permission` ( 
    `id` smallint unsigned AUTO_INCREMENT,
    `permission` varchar(50) NOT NULL,

    PRIMARY KEY (`id`)
);

-- Creating table: 'user'
CREATE TABLE `apartment_manager_db`.`user` (
    `id` int unsigned AUTO_INCREMENT,
    `creation_datetime` datetime NOT NULL,
    `user_name` varchar(50) NOT NULL,
    `password` varchar(50) NOT NULL,
    `permission_id` smallint unsigned NOT NULL,
    `notes` text,

    PRIMARY KEY (`id`),
    CONSTRAINT `fk_user_user_permission` FOREIGN KEY (`permission_id`) REFERENCES user_permission(`id`) ON DELETE CASCADE
);

-- Creating table: 'action'
CREATE TABLE `apartment_manager_db`.`action` (
    `id` int unsigned AUTO_INCREMENT,
    `creation_datetime` datetime NOT NULL,
    `user_id` int unsigned NOT NULL,
    `description` text NOT NULL,

    PRIMARY KEY (`id`),
    CONSTRAINT `fk_action_user` FOREIGN KEY (`user_id`) REFERENCES user(`id`) ON DELETE CASCADE
);

-- Inserting data into: 'employee_category'
INSERT INTO `apartment_manager_db`.`employee_category`(`category`) VALUES ('Host'), ('Cleaner');

-- Inserting data into: 'service_type'
INSERT INTO `apartment_manager_db`.`service_type`(`type`) VALUES ('Day-time'), ('Night-time'), ('Weekend'), ('Holiday');

-- Inserting data into: 'service_category'
INSERT INTO `apartment_manager_db`.`service_category`(`category`) VALUES ('Check-in'), ('Check-out'), ('Cleaning'), ('Extra');

-- Inserting data into: 'user_permission'
INSERT INTO `apartment_manager_db`.`user_permission`(`permission`) VALUES ('Administrator'), ('User'), ('Guest');
