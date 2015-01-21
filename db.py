import sqlite3

import config

conn = sqlite3.connect(config.MAIL_DB)
conn.row_factory = sqlite3.Row

def get_credentials():
	credentials = {}
	for row in conn.execute('SELECT type, value FROM credentials'):
		credentials[row['type']] = row['value']
	return credentials

def set_credentials(access_token, refresh_token=None):
	with conn as c:
		c.execute('INSERT OR REPLACE INTO credentials (type, value) VALUES("access_token", ?)', (access_token,))
		if refresh_token:
			c.execute('INSERT OR REPLACE INTO credentials (type, value) VALUES("refresh_token", ?)', (refresh_token,))

def update_labels(labels):
	args = []
	for label_id, label in labels.items():
		args.append((label_id, label['name'],
				label['message_list_visibility'], label['label_list_visibility']))
	conn.executemany('''
		INSERT OR REPLACE INTO labels
			(gmail_id, name, message_list_visibility, label_list_visibility)
			VALUES(?, ?, ?, ?)
	''', args)

def update_messages(messages):
	messages_args = []
	message_labels_args = []
	for message_id, message in messages.items():
		messages_args.append((message_id, message['history_id'], message['thread_id'],
				message['headers'], message['body']))
		for label_id in message['labels']:
			message_labels_args.append((label_id, message_id))
	conn.executemany('''
		INSERT INTO messages (gmail_id, history_id, thread_id, headers, body) VALUES(?, ?, ?, ?, ?)
	''', messages_args)
	conn.executemany('''
		INSERT INTO message_labels (label_id, message_id) VALUES(?, ?)
	''', message_labels_args)
