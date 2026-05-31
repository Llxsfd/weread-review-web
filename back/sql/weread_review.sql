
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for books
-- ----------------------------
DROP TABLE IF EXISTS `books`;
CREATE TABLE `books`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) DEFAULT NULL,
  `book_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `author` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `cover` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `category` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `reading_progress` int(0) NOT NULL,
  `marked_status` int(0) NOT NULL,
  `note_count` int(0) NOT NULL,
  `review_count` int(0) NOT NULL,
  `bookmark_count` int(0) NOT NULL,
  `last_note_sort` int(0) DEFAULT NULL,
  `last_synced_at` datetime(0) DEFAULT NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_books_user_book`(`user_id`, `book_id`) USING BTREE,
  INDEX `ix_books_book_id`(`book_id`) USING BTREE,
  INDEX `ix_books_title`(`title`) USING BTREE,
  INDEX `ix_books_user_id`(`user_id`) USING BTREE,
  CONSTRAINT `books_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 510 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for chapters
-- ----------------------------
DROP TABLE IF EXISTS `chapters`;
CREATE TABLE `chapters`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) DEFAULT NULL,
  `book_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `chapter_uid` int(0) NOT NULL,
  `chapter_idx` int(0) DEFAULT NULL,
  `title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_chapter_user_book_uid`(`user_id`, `book_id`, `chapter_uid`) USING BTREE,
  INDEX `ix_chapters_user_id`(`user_id`) USING BTREE,
  INDEX `ix_chapters_book_id`(`book_id`) USING BTREE,
  INDEX `ix_chapters_user_book_uid`(`user_id`, `book_id`, `chapter_uid`) USING BTREE,
  CONSTRAINT `chapters_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4446 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for collection_highlights
-- ----------------------------
DROP TABLE IF EXISTS `collection_highlights`;
CREATE TABLE `collection_highlights`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(0) NOT NULL,
  `collection_id` bigint(0) NOT NULL,
  `highlight_id` bigint(0) NOT NULL,
  `created_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_collection_highlight`(`user_id`, `collection_id`, `highlight_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for collections
-- ----------------------------
DROP TABLE IF EXISTS `collections`;
CREATE TABLE `collections`  (
  `id` bigint(0) NOT NULL AUTO_INCREMENT,
  `user_id` bigint(0) NOT NULL,
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for highlights
-- ----------------------------
DROP TABLE IF EXISTS `highlights`;
CREATE TABLE `highlights`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) DEFAULT NULL,
  `book_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `bookmark_id` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `chapter_uid` int(0) DEFAULT NULL,
  `chapter_title` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `mark_text` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `highlight_range` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `color_style` int(0) DEFAULT NULL,
  `created_at_weread` datetime(0) DEFAULT NULL,
  `weread_url` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_highlights_user_bookmark`(`user_id`, `bookmark_id`) USING BTREE,
  INDEX `ix_highlights_book_id`(`book_id`) USING BTREE,
  INDEX `ix_highlights_user_id`(`user_id`) USING BTREE,
  INDEX `ix_highlights_bookmark_id`(`bookmark_id`) USING BTREE,
  CONSTRAINT `highlights_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 10065 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for review_cards
-- ----------------------------
DROP TABLE IF EXISTS `review_cards`;
CREATE TABLE `review_cards`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) DEFAULT NULL,
  `highlight_id` int(0) NOT NULL,
  `question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `summary` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `memory_level` int(0) NOT NULL,
  `difficulty` int(0) NOT NULL,
  `review_count` int(0) NOT NULL,
  `last_reviewed_at` datetime(0) DEFAULT NULL,
  `next_review_at` datetime(0) NOT NULL,
  `status` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_review_cards_highlight_id`(`highlight_id`) USING BTREE,
  INDEX `ix_review_cards_status`(`status`) USING BTREE,
  INDEX `ix_review_cards_user_id`(`user_id`) USING BTREE,
  INDEX `ix_review_cards_next_review_at`(`next_review_at`) USING BTREE,
  CONSTRAINT `review_cards_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `review_cards_ibfk_2` FOREIGN KEY (`highlight_id`) REFERENCES `highlights` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 10065 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for review_logs
-- ----------------------------
DROP TABLE IF EXISTS `review_logs`;
CREATE TABLE `review_logs`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) DEFAULT NULL,
  `review_card_id` int(0) NOT NULL,
  `rating` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `previous_next_review_at` datetime(0) DEFAULT NULL,
  `next_review_at` datetime(0) NOT NULL,
  `created_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_review_logs_review_card_id`(`review_card_id`) USING BTREE,
  INDEX `ix_review_logs_user_id`(`user_id`) USING BTREE,
  CONSTRAINT `review_logs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `review_logs_ibfk_2` FOREIGN KEY (`review_card_id`) REFERENCES `review_cards` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 154 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for settings
-- ----------------------------
DROP TABLE IF EXISTS `settings`;
CREATE TABLE `settings`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) DEFAULT NULL,
  `key` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `value` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_secret` int(0) NOT NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_settings_user_key`(`user_id`, `key`) USING BTREE,
  INDEX `ix_settings_user_id`(`user_id`) USING BTREE,
  INDEX `ix_settings_key`(`key`) USING BTREE,
  CONSTRAINT `settings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for sync_jobs
-- ----------------------------
DROP TABLE IF EXISTS `sync_jobs`;
CREATE TABLE `sync_jobs`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) DEFAULT NULL,
  `job_type` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `status` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `message` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `books_synced` int(0) NOT NULL,
  `highlights_synced` int(0) NOT NULL,
  `started_at` datetime(0) NOT NULL,
  `finished_at` datetime(0) DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_sync_jobs_job_type`(`job_type`) USING BTREE,
  INDEX `ix_sync_jobs_user_id`(`user_id`) USING BTREE,
  INDEX `ix_sync_jobs_status`(`status`) USING BTREE,
  CONSTRAINT `sync_jobs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 14 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user_notes
-- ----------------------------
DROP TABLE IF EXISTS `user_notes`;
CREATE TABLE `user_notes`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) DEFAULT NULL,
  `book_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `review_id` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `chapter_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `star` int(0) DEFAULT NULL,
  `created_at_weread` datetime(0) DEFAULT NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `uq_user_notes_user_review`(`user_id`, `review_id`) USING BTREE,
  INDEX `ix_user_notes_user_id`(`user_id`) USING BTREE,
  INDEX `ix_user_notes_review_id`(`review_id`) USING BTREE,
  INDEX `ix_user_notes_book_id`(`book_id`) USING BTREE,
  CONSTRAINT `user_notes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 466 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `nickname` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime(0) NOT NULL,
  `updated_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `ix_users_email`(`email`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for highlight_ai_chats
-- ----------------------------
DROP TABLE IF EXISTS `highlight_ai_chats`;
CREATE TABLE `highlight_ai_chats`  (
  `id` int(0) NOT NULL AUTO_INCREMENT,
  `user_id` int(0) NOT NULL,
  `highlight_id` int(0) NOT NULL,
  `role` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `prompt_tokens` int(0) NOT NULL DEFAULT 0,
  `completion_tokens` int(0) NOT NULL DEFAULT 0,
  `created_at` datetime(0) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `ix_highlight_ai_chats_user_id`(`user_id`) USING BTREE,
  INDEX `ix_highlight_ai_chats_highlight_id`(`highlight_id`) USING BTREE,
  INDEX `idx_user_highlight`(`user_id`, `highlight_id`) USING BTREE,
  CONSTRAINT `highlight_ai_chats_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `highlight_ai_chats_ibfk_2` FOREIGN KEY (`highlight_id`) REFERENCES `highlights` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
