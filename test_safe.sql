-- Safe SQL statements for testing
SELECT * FROM users WHERE id = 1;

UPDATE users
SET last_login = NOW()
WHERE id = 123;

DELETE FROM sessions
WHERE expired_at < NOW();
