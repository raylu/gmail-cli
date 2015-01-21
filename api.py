import os
import subprocess
import urllib.parse

import requests

import config
import db

rs = requests.Session()

def authorize():
	credentials = db.get_credentials()
	if credentials:
		return credentials

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
	db.set_credentials(data['access_token'], data['refresh_token'])
	return data

class API:
	def __init__(self, access_token, refresh_token):
		self.access_token = access_token
		self.refresh_token = refresh_token

	def get(self, *endpoint, **params):
		url = 'https://www.googleapis.com/gmail/v1/users/me/' + '/'.join(endpoint)
		headers = {'Authorization': 'Bearer ' + self.access_token}

		camel_case_params = {}
		for k, v in params.items():
			split = k.split('_')
			k = split[0] + ''.join(map(str.capitalize, split[1:]))
			camel_case_params[k] = v

		response = rs.get(url, headers=headers, params=camel_case_params)
		data = response.json()
		error = data.get('error')
		if error:
			if error['code'] != 401:
				raise Exception(error)
			self.refresh()
			headers['Authorization'] = 'Bearer ' + self.access_token
			response = rs.get(url, headers=headers, params=camel_case_params)
			data = response.json()
			error = data.get('error')
			if error:
				raise Exception(error)
		return data

	def refresh(self):
		response = rs.post('https://www.googleapis.com/oauth2/v3/token', data={
			'refresh_token': self.refresh_token,
			'client_id': config.CLIENT_ID,
			'client_secret': config.CLIENT_SECRET,
			'grant_type': 'refresh_token',
		})
		self.access_token = response.json()['access_token']
		db.set_credentials(self.access_token)
