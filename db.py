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
	parsed_labels = {}
	with conn as c:
		for label in labels:
			unread = label.get('threadsUnread') or label.get('messagesUnread', 0)

			message_list_visibility = label.get('messageListVisibility', 'show')
			if message_list_visibility == 'show':
				message_list_visibility = 1
			elif message_list_visibility == 'hide':
				message_list_visibility = 0
			else:
				raise Exception(message_list_visibility)

			label_list_visibility = label.get('labelListVisibility', 'labelShow')
			if label_list_visibility == 'labelShow':
				label_list_visibility = 1
			elif label_list_visibility == 'labelShowIfUnread' and unread:
				label_list_visibility = 1
			elif label_list_visibility == 'labelHide':
				label_list_visibility = 0

			parsed_labels[label['id']] = {
				'name': label['name'],
				'message_list_visibility': message_list_visibility,
				'label_list_visibility': label_list_visibility,
				'unread': unread,
			}

			c.execute('''
				INSERT OR REPLACE INTO labels
					(gmail_id, name, message_list_visibility, label_list_visibility)
					VALUES(?, ?, ?, ?)
			''', (label['id'], label['name'], message_list_visibility, label_list_visibility))
	return parsed_labels
