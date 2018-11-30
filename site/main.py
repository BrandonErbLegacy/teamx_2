from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from threading import Thread
from flask import Flask, request, render_template, make_response

import json
import functools

from objects.mainobjects import *

import os
import psutil

app = Flask(__name__)
db_engine = create_engine('sqlite:///storage/master.db', connect_args={'check_same_thread':False})
session_maker = sessionmaker()
session_maker.configure(bind=db_engine)

main_session = session_maker()


def auth_endpoint(f):
	def wrap(*args, **kwargs):
		val = f()
		return val
	return wrap

#def login_required(func):
#    """Make sure user is logged in before proceeding"""
#    @functools.wraps(func)
#    def wrapper_login_required(*args, **kwargs):
#        if g.user is None:
#            return redirect(url_for("login", next=request.url))
#        return func(*args, **kwargs)
#    return wrapper_login_required

def admin_endpoint(f):
	@functools.wraps(f)
	def wrap(*args, **kwargs):
		if (request.cookies.get('teamx_session')):
			user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
			if (user):
				if (user.is_admin or user.is_superuser):
					request.teamx_user = user
					return f()
		return render_template('users/login.html', title='Home', user=None)
	return wrap

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

@app.route('/faq')
def faq():
	if (request.cookies.get('teamx_session')):
		user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
		if (user):
			return render_template('faqs.html', title='FAQs', user=user)
	return render_template('faqs.html', title='FAQs', user=None)


###############################
##### Dynamic Site Routes #####
###############################
@app.route('/register')
def user_register():
	return render_template('users/register.html', title='Register to become a user', user=None)

@app.route('/welcome')
def welcome_user():
	if (request.cookies.get('teamx_session')):
		user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
		if (user):
			return render_template('users/welcome.html', title='Welcome to Team X', user=user, servers=Server.GetTopThree(main_session))
	return render_template('users/register.html', title='Register to become a user', user=None)

@app.route('/servers')
def view_all_servers():
	if (request.cookies.get('teamx_session')):
		user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
		if (user):
				return render_template('servers.html', title='Servers', user=user, servers=Server.GetAll(main_session))
	return render_template('servers.html', title='Servers', user=None, servers=Server.GetAll(main_session))


@app.route('/logout')
def logout():
	response = make_response(render_template('users/login.html', title="Please log in", user=None))
	response.set_cookie('teamx_session', '', expires=0)
	return response

@app.route('/login')
def login():
	return render_template('users/login.html', title="Please log in", user=None)


###############################
#####  Admin Site Routes  #####
###############################
@app.route('/admin')
@admin_endpoint
def admin_home():
	return render_template('admin/dashboard.html', title="Admin Dashboard", user=request.teamx_user)

@app.route('/admin/users')
@admin_endpoint
def admin_users():
	return render_template('admin/manage_users.html', title="Manage Users", user=request.teamx_user)

@app.route('/admin/servers')
@admin_endpoint
def admin_servers():
	return render_template('admin/manage_servers.html', title="Admin Dashboard", user=request.teamx_user, servers=Server.GetAll(main_session))

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

@app.route('/api/create/server', methods=['POST'])
@admin_endpoint
def api_create_server():
	try:
		name = get_value_or_blank(request, "name")
		address = get_value_or_blank(request, "address")
		mc_version = get_value_or_blank(request, "minecraft_version")
		path_to_technic = get_value_or_blank(request, "path_to_technic")
		path_to_image = ""
		shortdesc = get_value_or_blank(request, "shortdesc")
		fulldesc = get_value_or_blank(request, "fulldesc")
		server = Server.AddServer(main_session, name, path_to_image, path_to_technic, mc_version, address, shortdesc, fulldesc)
		return server.id, 200
	except RecordExists as ex:
		return "Your "+ex.field+" must be unique. That one is already in use", 500


#This is a solution until we have something like 10k-20k users
#After that, pagination needs to be considered
@app.route('/api/fetch/all_users', methods=['GET'])
@admin_endpoint
def api_get_all_users():
	try:
		return User.GetAllUsers(main_session)
	except:
		return "There was an error", 500

@app.route('/api/fetch/cpu_usage', methods=['GET'])
@admin_endpoint
def api_get_cpu_usage():
	return str(psutil.cpu_percent())

@app.route('/api/fetch/memory_usage', methods=['GET'])
@admin_endpoint
def api_get_memory_usage():
	return str(psutil.virtual_memory().percent)

@app.route('/api/fetch/number_open_tickets', methods=['GET'])
@admin_endpoint
def api_get_open_tickets():
	return str(1)

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
