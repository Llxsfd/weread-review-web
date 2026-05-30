CREATE TABLE IF NOT EXISTS `collections` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NULL,
  `name` VARCHAR(128) NOT NULL,
  `description` TEXT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  KEY `ix_collections_user_id` (`user_id`),
  KEY `ix_collections_name` (`name`),
  CONSTRAINT `fk_collections_user_id`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `uq_collections_user_name`
    UNIQUE (`user_id`, `name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `collection_highlights` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NULL,
  `collection_id` INT NOT NULL,
  `highlight_id` INT NOT NULL,
  `created_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  KEY `ix_collection_highlights_user_id` (`user_id`),
  KEY `ix_collection_highlights_collection_id` (`collection_id`),
  KEY `ix_collection_highlights_highlight_id` (`highlight_id`),
  CONSTRAINT `fk_collection_highlights_user_id`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
    ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `fk_collection_highlights_collection_id`
    FOREIGN KEY (`collection_id`) REFERENCES `collections` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_collection_highlights_highlight_id`
    FOREIGN KEY (`highlight_id`) REFERENCES `highlights` (`id`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `uq_collection_highlight_user`
    UNIQUE (`user_id`, `collection_id`, `highlight_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
