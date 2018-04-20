import ast
import base64
import ConfigParser
import requests
from requests_oauthlib import OAuth2Session

# setup config parser
configParser = ConfigParser.RawConfigParser()
configFilePath = 'credentials.txt'
configParser.read(configFilePath)

# Credentials you get from registering a new application
client_id = configParser.get('credentials', 'client_id')
client_secret = configParser.get('credentials', 'client_secret')

redirect_uri = 'http://localhost:8080'
scopes = ['activity', 'heartrate', 'location', 'nutrition', 'profile', 'settings', 'sleep', 'social', 'weight']
expires_in = 604800
response_type = "code" 

# OAuth endpoints given in the GitHub API documentation
authorization_base_url = 'https://www.fitbit.com/oauth2/authorize'
token_url = 'https://api.fitbit.com/oauth2/token'

# create encoding string
client_encoding_string = base64.encodestring(client_id + ":" + client_secret).replace('\n', '')

# clean redirect uri
redirect_uri_encoded = redirect_uri.replace(':', '%3A')
redirect_uri_encoded = redirect_uri_encoded.replace('/', '%2F')

# combine scope
scope = ""
for s in scopes:
	if scope == "":
		scope = s
	else:
		scope += '%20'
		scope += s

# combine to url
authorization_url = authorization_base_url + "?response_type=" + response_type + "&client_id=" + client_id + "&redirect_uri=" + redirect_uri_encoded + "&scope=" + scope + "&expires_in=" + str(expires_in)

print '\nPlease go here and authorize,\n\n', authorization_url, '\n\n'


# put in authorization code from redirect url
authorization_code = 'ec3dda3b5b9ae527ec6808220923c168e64b660f'


url = token_url

header = {	'Authorization': 'Basic ' + client_encoding_string,
			'Content-Type': 'application/x-www-form-urlencoded'}

params = {	'client_id': client_id,
			'grant_type': 'authorization_code',
			'redirect_uri': redirect_uri,
			'code': authorization_code }


# response = requests.post(url=url, headers=header, params=params)

# print response.headers
# print '\n\n\n'
# print response.content



# refresh token for fitbit
access_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI2R0g5SFYiLCJhdWQiOiIyMkNYM1IiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJhY3QgcnNldCBybG9jIHJ3ZWkgcmhyIHJudXQgcnBybyByc2xlIiwiZXhwIjoxNTI0MjYyNTY1LCJpYXQiOjE1MjQyMzM3NjV9.oJHimqPYqXjkPBDxigxIhzc8GwauQrcWrXeJlwz1YkI"
refresh_token = "c85825dbdd9a80b8b28bfc9a0508f5a3d0d0b9317b8bb5b3a5427e1511435005"


url =  token_url

header = {	'Authorization': 'Basic ' + client_encoding_string,
			'Content-Type': 'application/x-www-form-urlencoded'}

params = {	'grant_type': 'refresh_token',
			'refresh_token': refresh_token}


response = requests.post(url=url, headers=header, params=params)

print response.headers
print '\n\n\n'
print response.content

tokens = ast.literal_eval(response.content)

print ""
print 'access_token:', tokens['access_token']
print 'refresh_token:', tokens['refresh_token']
# print response.content['access_token']
# print response.content['refresh_token']
