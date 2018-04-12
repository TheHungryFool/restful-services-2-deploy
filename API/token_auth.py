"""
Module containing the decorator for token based authorization 
"""
import jwt
from functools import wraps
from flask import jsonify, request
from API import app
import requests
import json
from datetime import datetime, timedelta
import jwt

def token_required(actual_method):
	@wraps(actual_method)
	def decorated(*args, **kwargs):
		token = None		
		if 'x-access-token' in request.headers:
			token = request.headers['x-access-token']
		else:
			return jsonify({'message' : 'Access token missing!', 'status' : 'Failure'})
		current_user = ''
		try:
			data = jwt.decode(token, app.config['SECRET_KEY'])
		except:
			return jsonify({'message' : 'Invalid access token!(Decode)', 'status' : 'Failure'})
		if str(datetime.utcnow()) > data['expiry']:
			return jsonify({'message' : 'Access token expired!', 'status' : 'Failure'})
		send_data = {'userid' : data['userid']}
		headers = {'content-type': 'application/json', 'x-expiry-token' : expirytoken()}
		received = requests.post(app.config['DATA_BROKER_URL'] + 'checkuser/', headers = headers, data = json.dumps(send_data)).json()
		if received['status'] == 'Success':
			current_user = received['userid']
		else:
			return jsonify({'message' : 'Invalid access token!(User)', 'status' : 'Failure'})
		return actual_method(current_user, *args, **kwargs)
	return decorated

def expirytoken():
	token = jwt.encode({'expiry' : str(datetime.utcnow() + timedelta(minutes = 2))}, app.config['SECRET_KEY'])
	return token.decode('UTF-8')