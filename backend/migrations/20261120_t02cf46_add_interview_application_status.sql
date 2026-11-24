-- T02CF46: ensure the applications status enum supports the interview stage.
-- MySQL 8. Run once against the CareerHub database.
-- Existing values and rows are preserved; this only expands the enum definition.
ALTER TABLE applications
    MODIFY COLUMN status ENUM(
        'pending',
        'reviewed',
        'interview',
        'accepted',
        'rejected',
        'withdrawn'
    ) NOT NULL DEFAULT 'pending';
