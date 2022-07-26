-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema Wheelchairs
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema Wheelchairs
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `Wheelchairs` DEFAULT CHARACTER SET utf8 COLLATE utf8_bin ;
USE `Wheelchairs` ;

-- -----------------------------------------------------
-- Table `Wheelchairs`.`VibrationCumulativeData`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Wheelchairs`.`VibrationCumulativeData` (
  `ID` INT NOT NULL AUTO_INCREMENT,
  `LONGITUDE` VARCHAR(45) NULL DEFAULT NULL,
  `LATITUDE` VARCHAR(45) NULL DEFAULT NULL,
  `SCORE` INT NULL DEFAULT NULL,
  `BOUND` INT NULL DEFAULT NULL,
  PRIMARY KEY (`ID`))
ENGINE = InnoDB
AUTO_INCREMENT = 23
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


-- -----------------------------------------------------
-- Table `Wheelchairs`.`VibrationData`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `Wheelchairs`.`VibrationData` (
  `idVibrationData` INT NOT NULL AUTO_INCREMENT,
  `latitude` VARCHAR(45) NOT NULL,
  `longitude` VARCHAR(45) NOT NULL,
  `class` VARCHAR(45) NOT NULL,
  `timestamp` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`idVibrationData`),
  UNIQUE INDEX `idVibrationData_UNIQUE` (`idVibrationData` ASC) VISIBLE)
ENGINE = InnoDB
AUTO_INCREMENT = 227
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
