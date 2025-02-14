CREATE TABLE IF NOT EXISTS questions (
    id VARCHAR(255) PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    hint1 TEXT NOT NULL,
    hint2 TEXT NOT NULL,
    hint3 TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INT DEFAULT 0
);

INSERT INTO questions (id, category, hint1, hint2, hint3, answer) VALUES
('1', 'TEST', 'h1', 'h2', 'h3', 'ans'),
('2', 'TEST', 'h1', 'h2', 'h3', 'ans'),
('3', 'TEST', 'h1', 'h2', 'h3', 'ans'),
('4', 'TEST', 'h1', 'h2', 'h3', 'ans'),
('5', 'TEST', 'h1', 'h2', 'h3', 'ans'),
('6', 'TEST', 'h1', 'h2', 'h3', 'ans'),
('7', 'TEST', 'h1', 'h2', 'h3', 'ans'),
('8', 'TEST', 'h1', 'h2', 'h3', 'ans'),
('9', 'TEST', 'h1', 'h2', 'h3', 'ans'),
('10', 'TEST', 'h1', 'h2', 'h3', 'ans');


CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    username VARCHAR(100) NOT NULL
);

INSERT INTO users (id, username) VALUES
('1', 'user1'),
('2', 'user2'),
('3', 'user3');

CREATE TABLE IF NOT EXISTS user_question_store (
    user_id VARCHAR(255) REFERENCES users(id) ON DELETE CASCADE,
    question_id VARCHAR(255) REFERENCES questions(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, question_id)
);

INSERT INTO user_question_store (user_id, question_id) VALUES
('1', '1'),
('1', '2'),
('1', '3'),
('2', '4'),
('2', '5'),
('3', '7'),
('3', '8'),
('3', '9'),
('3', '10');
