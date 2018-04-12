"""
Routes and views for the flask application.
"""

from datetime import datetime, timedelta
from API import app
from flask import jsonify, request
import requests
import json
import jwt
from werkzeug import secure_filename
from werkzeug.security import check_password_hash
from API.token_auth import token_required, expirytoken
import os

@app.route('/')
def index():
    return 'REST APIs for transport-analytics-app'

"""
Authentication based on Basic HTTP Auth
Returns success message and accesstoken
"""
@app.route('/login/', methods = ['POST'])
def login():
	auth = request.authorization
	if not auth or not auth.username or not auth.password:
		return jsonify({'status' : 'Failure'})
	send_data = {'userid' : auth.username}
	headers = {'content-type' : 'application/json', 'x-expiry-token' : expirytoken()}
	received = requests.post(app.config['DATA_BROKER_URL'] + 'getpassword/', headers = headers, data = json.dumps(send_data)).json()
	try:
	    check = received['password']
	except:
		return jsonify({'message' : received['message']})
	if check_password_hash(received['password'], auth.password):
		headers = {'content-type': 'application/json', 'x-expiry-token' : expirytoken()}
		received = requests.post(app.config['DATA_BROKER_URL'] + 'getuserdetails/', headers = headers, data = json.dumps(send_data)).json()
		if received['status'] == 'Failure':
			return jsonify({'message' : received['message'], 'status' : 'Failure'})
		accesstoken = jwt.encode({'userid' : auth.username, 'expiry' : str(datetime.utcnow() + timedelta(days = 100))}, app.config['SECRET_KEY'])
		response = jsonify({'status' : 'Success', 'access-token' : accesstoken.decode('UTF-8'), 'name' : received['name'], 'phone' : received['phone'], 'email' : received['email']})
		response.status_code = 201
		return response
	else:
		return jsonify({'status' : 'Failure', 'message' : 'Invalid Password'})

"""
API to get the details of a logged-in user
Takes in the userid and returns the details
"""
@app.route('/getuserdetails/', methods = ['POST'])
@token_required
def getuserdetails(current_user):
	send_data = {"userid" : current_user}
	headers = {'content-type': 'application/json', 'x-expiry-token' : expirytoken()}
	received = requests.post(app.config['DATA_BROKER_URL'] + 'getuserdetails/', headers = headers, data = json.dumps(send_data)).json()
	if received['status'] == 'Failure':
		return jsonify({'message' : received['message'], 'status' : 'Failure'})
	response = jsonify(received) 
	response.status_code = 201
	return response

"""
API to upload the files of a logged-in user
"""
@app.route('/uploadfile/', methods = ['POST', 'GET'])
@token_required
def uploadfile(current_user):
	if request.method == 'POST':
		folder = os.path.join(app.config['UPLOAD_FOLDER'],current_user)
		file = request.files['file']
		if not os.path.isdir(folder):
			os.mkdir(folder)
			os.chmod(folder,0o777)	
		prefix = str(datetime.utcnow())
		prefix = prefix.replace(' ','')	
		prefix = prefix.replace(':','-')
		prefix = prefix.replace('.','-')		
		target = os.path.join(folder, prefix + secure_filename(file.filename))
		file.save(target)	
		os.chmod(target,0o777)	
		send_data = {
		'userid' : current_user,
		'filename' : secure_filename(file.filename),
		'uploadid' : current_user + prefix + secure_filename(file.filename),
		'storedname' : prefix + secure_filename(file.filename)
		}
		headers = {'content-type': 'application/json', 'x-expiry-token' : expirytoken()}
		received = requests.post(app.config['DATA_BROKER_URL'] + 'addupload/', headers = headers, data = json.dumps(send_data)).json()
		if received['status'] == 'Failure' or not received:
			return jsonify({'message' : 'Unable to process upload','status' : 'Failure'})
		return jsonify({'status' : 'Success','message' : 'File uploaded successfuly!'})
	else: 
		return jsonify({'message' : 'Unable to process upload','status' : 'Failure'})