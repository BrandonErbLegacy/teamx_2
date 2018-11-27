from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from threading import Thread
from flask import Flask, request, render_template, make_response

import json

from objects.mainobjects import *

app = Flask(__name__)
db_engine = create_engine('sqlite:///storage/master.db', connect_args={'check_same_thread':False})
session_maker = sessionmaker()
session_maker.configure(bind=db_engine)

main_session = session_maker()


##############################
##### Static Site Routes #####
##############################

@app.route('/')
@app.route('/index')
def index():
	if (request.cookies.get('teamx_session')):
		user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
		if (user):
			return render_template('index.html', title='Home', user=user)
	return render_template('index.html', title='Home', user=None)

@app.route('/about')
def about():
	return "<html>About</html>"

@app.route('/contact')
def contact():
	return "<html>Contact</html>"


###############################
##### Dynamic Site Routes #####
###############################
@app.route('/register')
def user_register():
	return render_template('register.html', title='Register to become a user', user=None)

@app.route('/welcome')
def welcome_user():
	if (request.cookies.get('teamx_session')):
		user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
		if (user):
			return render_template('welcome.html', title='Welcome to Team X', user=user)
	return render_template('register.html', title='Register to become a user', user=None)

@app.route('/logout')
def logout():
	response = make_response(render_template('login.html', title="Please log in", user=None))
	response.set_cookie('teamx_session', '', expires=0)
	return response

@app.route('/login')
def login():
	return render_template('login.html', title="Please log in", user=None)


###############################
#####  Admin Site Routes  #####
###############################

@app.route('/admin')
def admin_login():
	return "Admin login or redirect"

###############################
#####   Rest API Routes   #####
###############################
@app.route('/api/authentication/user', methods=['POST'])
def api_auth_user():
	username = get_value_or_blank(request, "username")
	password = get_value_or_blank(request, "password")

	if (username == "" or password == ""):
		return "Both fields cannot be blank", 403
	else:
		session = User.LogUserIn(main_session, username, password, request.remote_addr)
		if session == None:
			return "The provided credentials did not match our records", 403
		else:
			return session.id, 200

@app.route('/api/create/user', methods=['POST'])
def api_create_user():
	try:
		username = get_value_or_blank(request, "username")
		password = get_value_or_blank(request, "password")
		display_name = get_value_or_blank(request, "display_name")
		first_name = get_value_or_blank(request, "first_name")
		email = get_value_or_blank(request, "email")
		user, session_id = User.RegisterUser(main_session, username, password, display_name, first_name, email, request.remote_addr)
		return session_id, 200
	except RecordExists as ex:
		return "Your "+ex.field+" must be unique. That one is already in use", 500

###############################
#####  Utility Functions  #####
###############################
def get_value_or_blank(request, value, type="POST"):
	#Returns either the value pulled from a request. Or defaults to nothing
	if (type == "POST"):
		return "" if request.form.get(value) is None else request.form.get(value)
	else:
		raise NotImplemented

DatabaseBase.metadata.create_all(db_engine)
main_session.commit()

app.run(debug=True)
