SELECT id, name FROM users WHERE age > 21;
INSERT INTO logs (id, message) VALUES (1, 'hello');
UPDATE users SET status = 'inactive';
UPDATE users SET status = 'inactive' WHERE user_id = 123;
DELETE FROM logs;
DELETE FROM logs WHERE created_at < '2023-01-01';
SELECT * FROM users;
INSERT INTO users (name) VALUES ('John');
