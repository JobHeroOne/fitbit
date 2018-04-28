#!/usr/bin/env python2

import ast
import base64
import ConfigParser
import datetime
import requests

class Oauth():
	'''
	Handels the OAuth2.0
	'''

	def __init__(self):

		# default settings
		self.authorization_base_url = 'https://www.fitbit.com/oauth2/authorize'
		self.token_url = 'https://api.fitbit.com/oauth2/token'
		
		self.redirect_uri = 'http://localhost:8080'
		self.redirect_uri_encoded = self.url_encode(self.redirect_uri)
		
		self.scopes = ['activity', 'heartrate', 'location', 'nutrition', 'profile', 'settings', 'sleep', 'social', 'weight']
		self.expires_in = 604800
		self.expires = ""
		
		self.response_type = "code" 


	def create_config_file(self):
		'''
		Creates an emtpy config file, overwrites any existing values.
		'''

		# Setup config parser
		configParser = ConfigParser.ConfigParser()

		# add tokens to config file
		configParser.add_section('credentials')
		configParser.set('credentials', 'client_id', "")
		configParser.set('credentials', 'client_secret', "")
		configParser.set('credentials', 'redirect_url', "")

		configParser.add_section('authorization')
		configParser.set('authorization', 'authorization_code', "")

		configParser.add_section('tokens')
		configParser.set('tokens', 'access_token', "")
		configParser.set('tokens', 'refresh_token', "")
		configParser.set('tokens', 'expires', "")
		
		# write changes to config file
		with open('config.txt', 'wb') as config_file:
			configParser.write(config_file)		


	def url_encode(self, input_string):
		'''
		converts a string to url encoding
		'''

		# reserved chars to be replaced by encoding
		replace_char = {"=":"%3D", "!":"%21", "*":"%2A", "'":"%27", "(":"%28", ")":"%29", ";":"%3B", ":":"%3A", "@":"%40", "&":"%26", "+":"%2B", "$":"%24", ",":"%2C", "/":"%2F", "?":"%3F", "#":"%23", "[":"%5B", "]":"%5D", " ":"%20", '"':"%20", "-":"%2D", ".":"%2E", "<":"%3C", ">":"%3E", '\\':"%5C", "^":"%5E", "_":"%5F", "`":"%60", "{":"%7B", "|":"%7C", "}":"%7D", "~":"%7E"} 
		
		# replace % first
		input_string = input_string.replace("%","%25")

		# replace all other characters
		for k,v in replace_char.items():
			input_string = input_string.replace(k, v)

		# return encoded
		return input_string


	def combine_scope(self):
		'''
		combined the list of scopes toa url friedly list
		'''
		
		return self.url_encode(' '.join(self.scopes))


	def load_credentials(self):
		'''
		Gets the credentials from the config file using configparser
		'''

		# Setup config parser
		configParser = ConfigParser.RawConfigParser()
		configFilePath = 'config.txt'
		configParser.read(configFilePath)
		
		# Get credentials
		self.client_id = configParser.get('credentials', 'client_id')
		self.client_secret = configParser.get('credentials', 'client_secret')
		self.client_encoding_string = base64.encodestring(self.client_id + ":" + self.client_secret).replace('\n', '')


	def get_authorization_url(self):
		'''
		Returns the authorization url for the end user
		'''

		return self.authorization_base_url + "?response_type=" + self.response_type + "&client_id=" + self.client_id + "&redirect_uri=" + self.redirect_uri_encoded + "&scope=" + self.combine_scope() + "&expires_in=" + str(self.expires_in)


	def load_authorization(self):
		'''
		Gets the authorization_code from the config file using configparser
		'''

		# Setup config parser
		configParser = ConfigParser.RawConfigParser()
		configFilePath = 'config.txt'
		configParser.read(configFilePath)
		
		# Get authorization_code
		self.authorization_code = configParser.get('authorization', 'authorization_code')


	def get_tokens(self):
		'''
		Gets the access token and refresh token from the fitbit server
		'''
		
		# setup of question url
		url = self.token_url

		headers = {	'Authorization': 'Basic ' + self.client_encoding_string,
					'Content-Type': 'application/x-www-form-urlencoded'}

		params = {	'client_id': self.client_id,
					'grant_type': 'authorization_code',
					'redirect_uri': self.redirect_uri,
					'code': self.authorization_code}

		# post question to server
		response = requests.post(url=url, headers=headers, params=params)
		
		# convert response to literal dict
		tokens = ast.literal_eval(response.content)

		# extract tokens from dict
		self.access_token = tokens['access_token']
		self.refresh_token = tokens['refresh_token']
		self.expires = str(datetime.datetime.now() + datetime.timedelta(seconds=int(tokens['expires_in'])))

		# Setup config parser
		configParser = ConfigParser.ConfigParser()
		configFilePath = 'config.txt'
		configParser.read(configFilePath)

		# add tokens to config file
		configParser.set('tokens', 'access_token', self.access_token)
		configParser.set('tokens', 'refresh_token', self.refresh_token)
		configParser.set('tokens', 'expires', self.expires)
		
		# write changes to config file
		with open('config.txt', 'wb') as config_file:
			configParser.write(config_file)


	def refresh_tokens(self):
		'''
		Gets the access token and refresh token from the fitbit server
		'''
		
		# setup of question url
		url = self.token_url

		headers = {	'Authorization': 'Basic ' + self.client_encoding_string,
					'Content-Type': 'application/x-www-form-urlencoded'}

		params = {	'grant_type': 'refresh_token',
					'refresh_token': self.refresh_token}

		# post question to server
		response = requests.post(url=url, headers=headers, params=params)

		# convert response to literal dict
		tokens = ast.literal_eval(response.content)

		# extract tokens from dict
		self.access_token = tokens['access_token']
		self.refresh_token = tokens['refresh_token']
		self.expires = str(datetime.datetime.now() + datetime.timedelta(seconds=int(tokens['expires_in'])))

		# Setup config parser
		configParser = ConfigParser.ConfigParser()
		configFilePath = 'config.txt'
		configParser.read(configFilePath)

		# add tokens to config file
		configParser.set('tokens', 'access_token', self.access_token)
		configParser.set('tokens', 'refresh_token', self.refresh_token)
		configParser.set('tokens', 'expires', self.expires)
		
		# write changes to config file
		with open('config.txt', 'wb') as config_file:
			configParser.write(config_file)


	def load_tokens(self):
		'''
		Gets the tokens from the config file using configparser
		'''

		# Setup config parser
		configParser = ConfigParser.RawConfigParser()
		configFilePath = 'config.txt'
		configParser.read(configFilePath)
		
		# Get tokens
		self.access_token = configParser.get('tokens', 'access_token')
		self.refresh_token = configParser.get('tokens', 'refresh_token')
		self.expires =  configParser.get('tokens', 'expires')

		# check iftokens are still valid
		self.check_tokens()


	def check_tokens(self):
		'''
		Checks if the currect tokens are still valid
		'''

		# check if the expiration date has passed, if so, refresh tokens
		if datetime.datetime.strptime(self.expires, '%Y-%m-%d %H:%M:%S.%f') < datetime.datetime.now():
			self.refresh_tokens()


class Fitbit():
	'''
	Handels the data requests to fitbit after authentication
	'''

	def __init__(self, access_token):

		# credentials
		self.access_token = access_token


	def update_url(self, url, values):
		'''
		updates and replaces base url with values

		url 	Base url that needs updating
		values	Dictionary containing key value pair that needs to be updated in the base url 
		'''

		# updating url with values
		for k,v in values.items():
			url = url.replace(k,v)

		return url


	def user_details(self, user_id='-'):
		''' 
		Requests the users profile and settings

		user-id		The encoded ID of the user. Use "-" (dash) for current logged-in user.
		'''

		url = "https://api.fitbit.com/1/user/[user_id]/profile.json" 

		# values to update
		values = {'[user_id]': user_id}

		# updating url with values
		url = self.update_url(url, values)

		# creating header
		headers = {"Authorization": "Bearer " + self.access_token.replace("\n", "")}

		# submitting request
		response = requests.get(url=url, headers=headers).content

		# response cleanup
		return ast.literal_eval(response)['user']


	def heart_rate_series(self, user_id='-', start_date='today', end_date='1d'):
		'''
		Requests the heartrate data

		user_id			The encoded ID of the user. Use "-" (dash) for current logged-in user.
		start_date		The start date of the range, in the format yyyy-MM-dd or today.
		end_date		The end date of the range, in the format yyyy-MM-dd or options are 1d, 7d, 30d, 1w, 1m.
		'''
		
		# base url
		url = "https://api.fitbit.com/1/user/[user_id]/activities/heart/date/[start_date]/[end_date].json"

		# values to update
		values = {'[user_id]': user_id, '[start_date]': start_date, '[end_date]': end_date}

		# updating url with values
		url = self.update_url(url, values)

		# creating header
		headers = {"Authorization": "Bearer " + self.access_token.replace("\n", "")}

		# submitting request
		response = requests.get(url=url, headers=headers).content

		# response cleanup
		return ast.literal_eval(response)['activities-heart'][0]['value']


	def heart_rate_intraday(self, user_id='-', start_date='today', end_time='1d', detail_level='1min'):
		'''
		Requests the heartrate data

		user_id			The encoded ID of the user. Use "-" (dash) for current logged-in user.
		start_date		The start date of the range, in the format yyyy-MM-dd or today.
		end-time		The end of the period, in the format HH:mm or options 1d.
		detail_level	Number of data points to include. Either 1sec or 1min.
		'''
		
		# base url
		url = "https://api.fitbit.com/1/user/[user_id]/activities/heart/date/[start_date]/[end_time]/[detail_level].json"

		# values to update
		values = {'[user_id]': user_id, '[start_date]': start_date, '[end_time]': end_time, '[detail_level]': detail_level}

		# updating url with values
		url = self.update_url(url, values)

		# creating header
		headers = {"Authorization": "Bearer " + self.access_token.replace("\n", "")}

		# submitting request
		response = requests.get(url=url, headers=headers).content

		# response cleanup
		return ast.literal_eval(response)['activities-heart-intraday']['dataset']


def main():
	login = Oauth()

	# login.create_config_file()

	# login.load_credentials()

	# print login.get_authorization_url()

	# login.load_authorization()

	# login.get_tokens()

	login.load_tokens()

	fitbit = Fitbit(login.access_token)

	print (fitbit.heart_rate_intraday())



if __name__ == "__main__":
	main()
