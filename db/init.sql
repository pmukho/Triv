CREATE TABLE IF NOT EXISTS questions (
    id VARCHAR(255) PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    hint1 TEXT NOT NULL,
    hint2 TEXT NOT NULL,
    hint3 TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usage_count INT DEFAULT 0,
    downvote_count INT DEFAULT 0
);

INSERT INTO questions (id, category, hint1, hint2, hint3, answer) VALUES
('1', 'CAT1', 'h1', 'h2', 'h3', 'ans'),
('2', 'CAT1', 'h1', 'h2', 'h3', 'ans'),
('3', 'CAT1', 'h1', 'h2', 'h3', 'ans'),
('4', 'CAT1', 'h1', 'h2', 'h3', 'ans'),
('5', 'CAT1', 'h1', 'h2', 'h3', 'ans'),
('6', 'CAT1', 'h1', 'h2', 'h3', 'ans'),
('7', 'CAT1', 'h1', 'h2', 'h3', 'ans'),
('8', 'CAT1', 'h1', 'h2', 'h3', 'ans'),
('9', 'CAT1', 'h1', 'h2', 'h3', 'ans'),
('10', 'CAT1', 'h1', 'h2', 'h3', 'ans'),
('11', 'CAT2', 'h1', 'h2', 'h3', 'ans'),
('12', 'CAT2', 'h1', 'h2', 'h3', 'ans'),
('13', 'CAT2', 'h1', 'h2', 'h3', 'ans'),
('14', 'CAT2', 'h1', 'h2', 'h3', 'ans'),
('15', 'CAT2', 'h1', 'h2', 'h3', 'ans'),
('16', 'CAT2', 'h1', 'h2', 'h3', 'ans'),
('17', 'CAT2', 'h1', 'h2', 'h3', 'ans'),
('18', 'CAT2', 'h1', 'h2', 'h3', 'ans'),
('19', 'CAT2', 'h1', 'h2', 'h3', 'ans'),
('20', 'CAT2', 'h1', 'h2', 'h3', 'ans');


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

CREATE TABLE IF NOT EXISTS wiki_articles (
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    PRIMARY KEY (title, category)
);

COPY wiki_articles(title, category) 
FROM '/docker-entrypoint-initdb.d/data/wiki_articles.csv' 
DELIMITER ',' CSV HEADER;