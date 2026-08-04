-- MySQL schema generated from SQLite data

CREATE DATABASE IF NOT EXISTS `catchhot` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `catchhot`;

CREATE TABLE IF NOT EXISTS `tags` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `keyword` VARCHAR(200) NOT NULL,
  `keywords` JSON DEFAULT NULL,
  `platforms` JSON DEFAULT NULL,
  `interval_minutes` INT NOT NULL DEFAULT 60,
  `enabled` TINYINT(1) NOT NULL DEFAULT 1,
  `deleted` TINYINT(1) NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL,
  `updated_at` DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `jobs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `tag_id` INT NOT NULL,
  `platform` VARCHAR(50) NOT NULL,
  `status` VARCHAR(20) NOT NULL,
  `retry_count` INT NOT NULL DEFAULT 0,
  `items_fetched` INT NOT NULL DEFAULT 0,
  `items_saved` INT NOT NULL DEFAULT 0,
  `error_message` TEXT,
  `started_at` DATETIME NOT NULL,
  `finished_at` DATETIME DEFAULT NULL,
  FOREIGN KEY (`tag_id`) REFERENCES `tags`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `hot_items` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `tag_id` INT NOT NULL,
  `platform` VARCHAR(50) NOT NULL,
  `title` VARCHAR(500) NOT NULL,
  `url` TEXT NOT NULL,
  `summary` TEXT DEFAULT NULL,
  `published_at` DATETIME DEFAULT NULL,
  `hot_score` DOUBLE NOT NULL DEFAULT 0.0,
  `score` DOUBLE NOT NULL DEFAULT 0.0,
  `meta` JSON DEFAULT NULL,
  `fingerprint` VARCHAR(64) NOT NULL,
  `fetched_at` DATETIME NOT NULL,
  FOREIGN KEY (`tag_id`) REFERENCES `tags`(`id`) ON DELETE CASCADE,
  UNIQUE KEY `uq_tag_fingerprint` (`tag_id`,`fingerprint`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
