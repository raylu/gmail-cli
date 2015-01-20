DROP TABLE IF EXISTS message_labels;
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS threads;
DROP TABLE IF EXISTS labels;

CREATE TABLE credentials (
	type TEXT PRIMARY KEY,
	value TEXT
);

CREATE TABLE labels (
	gmail_id TEXT PRIMARY KEY,
	name TEXT,
	message_list_visibility INTEGER,
	label_list_visibility INTEGER
);

CREATE TABLE threads (
	gmail_id TEXT PRIMARY KEY,
	history_id INTEGER
);

CREATE TABLE messages (
	gmail_id TEXT PRIMARY KEY,
	history_id INTEGER,
	thread_id TEXT REFERENCES threads(gmail_id),
	headers TEXT,
	body TEXT
);

CREATE TABLE message_labels (
	label_id TEXT REFERENCES labels(gmail_id),
	message_id TEXT REFERENCES messages(gmail_id)
);
