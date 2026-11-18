-- T02CF0E: add a persistent state for applications withdrawn by their owner.
-- MySQL 8. Run once after the T02CED7 application schema migration.
ALTER TABLE applications
    MODIFY COLUMN status ENUM('pending', 'reviewed', 'accepted', 'rejected', 'withdrawn') NOT NULL DEFAULT 'pending';
