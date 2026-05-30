ALTER TABLE settings
  ADD COLUMN user_id INT NULL AFTER id;

ALTER TABLE books
  ADD COLUMN user_id INT NULL AFTER id;

ALTER TABLE highlights
  ADD COLUMN user_id INT NULL AFTER id;

ALTER TABLE user_notes
  ADD COLUMN user_id INT NULL AFTER id;

ALTER TABLE review_cards
  ADD COLUMN user_id INT NULL AFTER id;

ALTER TABLE review_logs
  ADD COLUMN user_id INT NULL AFTER id;

ALTER TABLE sync_jobs
  ADD COLUMN user_id INT NULL AFTER id;

ALTER TABLE chapters
  ADD COLUMN user_id INT NULL AFTER id;

CREATE INDEX ix_settings_user_id ON settings (user_id);
CREATE INDEX ix_books_user_id ON books (user_id);
CREATE INDEX ix_highlights_user_id ON highlights (user_id);
CREATE INDEX ix_user_notes_user_id ON user_notes (user_id);
CREATE INDEX ix_review_cards_user_id ON review_cards (user_id);
CREATE INDEX ix_review_logs_user_id ON review_logs (user_id);
CREATE INDEX ix_sync_jobs_user_id ON sync_jobs (user_id);
CREATE INDEX ix_chapters_user_id ON chapters (user_id);

