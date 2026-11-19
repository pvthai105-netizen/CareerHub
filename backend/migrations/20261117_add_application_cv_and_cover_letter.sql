-- CareerHub / T02CED7
-- MySQL 8 migration: add CV path and optional cover letter to applications.
-- Run once against the CareerHub database after confirming both columns are absent.

ALTER TABLE applications
    ADD COLUMN cv_file_path VARCHAR(255) NULL,
    ADD COLUMN cover_letter TEXT NULL;
