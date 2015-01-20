import os
import subprocess
import urllib.parse

import requests

import config

rs = requests.Session()

def authorize():
	redirect_uri = 'urn:ietf:wg:oauth:2.0:oob' # https://developers.google.com/accounts/docs/OAuth2InstalledApp#choosingredirecturi
	url = 'https://accounts.google.com/o/oauth2/auth?' + urllib.parse.urlencode({
		'response_type': 'code',
		'client_id': config.CLIENT_ID,
		'redirect_uri': redirect_uri,
		'scope': 'https://www.googleapis.com/auth/gmail.modify',
	})
	devnull = open(os.devnull)
	subprocess.Popen(['x-www-browser', url], stdout=devnull, stderr=devnull)
	code = input('code: ')
	response = rs.post('https://www.googleapis.com/oauth2/v3/token', data={
		'code': code,
		'client_id': config.CLIENT_ID,
		'client_secret': config.CLIENT_SECRET,
		'redirect_uri': redirect_uri,
		'grant_type': 'authorization_code',
	})
	data = response.json()
	print('access_token:', data['access_token'])
	print('refresh_token:', data['refresh_token'])

class API:
	def __init__(self, access_token):
		self.access_token = access_token

	def get(self, endpoint):
		response = rs.get('https://www.googleapis.com/gmail/v1/users/me/' + endpoint,
				headers={'Authorization': 'Bearer ' + self.access_token})
		return response.json()
