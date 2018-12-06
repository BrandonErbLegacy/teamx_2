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

player_count_per_server = {}#Server_ID:player_count


def auth_endpoint(f):
	def wrap(*args, **kwargs):
		if (request.cookies.get('teamx_session')):
			user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
			if (user):
				request.teamx_user = user
		val = f(*args, **kwargs)
		return val
	return wrap

def admin_endpoint(f):
	@functools.wraps(f)
	def wrap(*args, **kwargs):
		if (request.cookies.get('teamx_session')):
			user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
			if (user):
				if (user.is_admin or user.is_superuser):
					request.teamx_user = user
					return f(*args, **kwargs)
		return render_template('users/login.html', title='Home', user=None)
	return wrap

def superuser_endpoint(f):
	@functools.wraps(f)
	def wrap(*args, **kwargs):
		if (request.cookies.get('teamx_session')):
			user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
			if (user):
				if (user.is_superuser):
					request.teamx_user = user
					return f(*args, **kwargs)
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
	user = None
	if (request.cookies.get('teamx_session')):
		user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
	return render_template('about.html', title='About us', user=user)

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

@app.route('/view_server/<string:server_id>', methods=["GET"])
def view_one_server(server_id):
	server = Server.GetById(main_session, server_id)
	if (request.cookies.get('teamx_session')):
		user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
		if (user):
			return render_template('view_server.html', title=server.name, user=user, server=server, mods=server.GetMods(main_session), updates=server.GetUpdates(main_session))
	return render_template('view_server.html', title=server.name, user=None, server=server, mods=server.GetMods(main_session), updates=server.GetUpdates(main_session))


@app.route('/logout')
def logout():
	response = make_response(render_template('users/login.html', title="Please log in", user=None))
	response.set_cookie('teamx_session', '', expires=0)
	return response

@app.route('/login')
def login():
	return render_template('users/login.html', title="Please log in", user=None)

@app.route('/contact')
def contact():
	if (request.cookies.get('teamx_session')):
		user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
		if (user):
			return render_template('contact.html', title='FAQs', user=user, tickets=Ticket.GetByUser(main_session, user), servers=Server.GetAll(main_session))
	return render_template('contact.html', title='FAQs', user=None, tickets=None, servers=Server.GetAll(main_session))

@app.route('/contact/<string:ticket_id>')
def contact_view_ticket(ticket_id):
	try:
		user = None
		if (request.cookies.get('teamx_session')):
			user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
		ticket = Ticket.GetTicketById(main_session, ticket_id, user)
		replies = Ticket.GetRepliesByTicket(main_session, ticket)
		return render_template('view_ticket.html', title='View ticket', user=user, ticket=ticket, replies=replies)
	except AttributeError:
		user = None
		if (request.cookies.get('teamx_session')):
			user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
		return render_template('view_ticket.html', title='View ticket', user=user, ticket=None, replies=[])

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

@app.route('/admin/tickets')
@admin_endpoint
def admin_ticket_center():
	return render_template('admin/ticket_center.html', title="Open Tickets", user=request.teamx_user, servers=Server.GetAll(main_session), tickets=Ticket.GetOpenTickets(main_session))

@app.route('/admin/ticket/<string:ticket_id>')
@admin_endpoint
def admin_view_ticket(ticket_id):
	user = request.teamx_user
	ticket = Ticket.GetTicketById(main_session, ticket_id, user)
	replies = Ticket.GetRepliesByTicket(main_session, ticket)
	return render_template('admin/view_ticket.html', title="Ticket "+ticket.title, user=user, servers=Server.GetAll(main_session), ticket=ticket, replies=replies)



################################
#####   Superuser Routes   #####
################################
@app.route('/superuser')
@superuser_endpoint
def superuser_home():
	return render_template('superuser/dashboard.html', title="Superuser Dashboard", user=request.teamx_user, users=User.GetAdminUsers(main_session))


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

@app.route('/api/exists/user', methods=['POST'])
def api_check_user():
	username = get_value_or_blank(request, "username")
	user = User.UserExists(main_session, username)
	if user != None:
		return user.id
	else:
		return "NONE", 200

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

@app.route('/api/create/ticket', methods=['POST'])
def api_create_ticket():
	try:
		user = None
		if (request.cookies.get('teamx_session')):
			user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
		title = get_value_or_blank(request, "title")
		server_id = get_value_or_blank(request, "server")
		reason = get_value_or_blank(request, "reason")
		ticket = Ticket.OpenTicket(main_session, user, title, reason, server_id)
		return ticket.id, 200
	except:
		return "There was an error creating your ticket", 500

@app.route('/api/close/ticket', methods=['POST'])
@auth_endpoint
def api_close_ticket():
	try:
		ticket_id = get_value_or_blank(request, "ticket_id")
		ticket = Ticket.GetTicketById(main_session, ticket_id, request.teamx_user)
		Ticket.CloseTicket(main_session, ticket)
		return "Ticket closed", 200
	except IOError:
		return "There was an error closing the ticket", 500

@app.route('/api/create/ticket_reply', methods=['POST'])
def api_create_ticket_reply():
	try:
		user = None
		if (request.cookies.get('teamx_session')):
			user = Session.GetUserBySession(main_session, request.cookies.get('teamx_session'))
		ticket_id = get_value_or_blank(request, "ticket_id")
		text = get_value_or_blank(request, "reply")
		ticket = Ticket.GetTicketById(main_session, ticket_id, user)
		comment = Ticket.CommentTicket(main_session, ticket, user, text)
		return comment.id
	except:
		return "There was an error creating your response", 500

@app.route('/api/server/event', methods=['POST'])
def api_server_create_event():
	data = json.loads(request.data)
	print(data)
	server_id = ""
	action = ""
	player_id = ""
	player_name = ""
	if ("server_id" in data.keys()):
		server_id = data["server_id"]
	if ("action" in data.keys()):
		action = data["action"]
	if ("player_id" in data.keys()):
		player_id = data["player_id"]
	if ("player_name" in data.keys()):
		player_name = data["player_name"]

	server = Server.GetById(main_session, server_id)
	if (action == "SERVER_STARTED"):
		ServerActivityLog.ServerStarted(main_session, server_id)
	elif (action == "SERVER_PLANNED_STOP"):
		ServerActivityLog.ServerStopped(main_session, server_id)
	elif (action == "SERVER_CRASHED"):
		ServerActivityLog.ServerCrashed(main_session, server_id)
	elif (action == "PLAYER_LOGGED_IN"):
		if (server_id in player_count_per_server.keys()):
			player_count_per_server[server_id] = player_count_per_server[server_id]+1
		else:
			player_count_per_server[server_id] = 1
		ServerActivityLog.AddServerActivityLog(main_session, action, server.id, player_id, player_name)
	elif (action == "PLAYER_LOGGED_OUT"):
		if (server_id in player_count_per_server.keys()):
			player_count_per_server[server_id] = player_count_per_server[server_id]-1
			if player_count_per_server[server_id] < 0:
				player_count_per_server[server_id] = 0
		ServerActivityLog.AddServerActivityLog(main_session, action, server.id, player_id, player_name)
	elif ("PLAYER_MAX" in action):
		ServerActivityLog.AddServerActivityLog(main_session, action, server.id, player_id, player_name, generate_mapping=False)
	else:
		ServerActivityLog.AddServerActivityLog(main_session, action, server.id, player_id, player_name)
	return "", 200

@app.route('/api/server/<string:server_id>/get_current_player_count', methods=['GET'])
def api_server_get_player_count(server_id):
	if (server_id in player_count_per_server.keys()):
		return str(player_count_per_server[server_id])
	else:
		player_count_per_server[server_id] = 0
		return str(0)

@app.route('/api/server/<string:server_id>/get_max_player_count', methods=['GET'])
def api_server_get_max_player_count(server_id):
	return ServerActivityLog.GetMaxPlayers(main_session, server_id)

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
	return str(Ticket.GetOpenCount(main_session))

@app.route('/api/give_admin/user', methods=['POST'])
@superuser_endpoint
def api_give_user_admin():
	user_id = get_value_or_blank(request, "user_id")
	if (user_id != ""):
		User.GiveAdmin(main_session, user_id)
	return "", 200

@app.route('/api/create/mod_reference', methods=['POST'])
@admin_endpoint
def api_create_mod_reference():
	try:
		name = get_value_or_blank(request, "name")
		version = get_value_or_blank(request, "version")
		server_id = get_value_or_blank(request, "server_id")
		Mod.AddMod(main_session, name, version, server_id)
		return "", 200
	except:
		return "There was an error adding that mod", 500

@app.route('/api/create/patch_reference', methods=['POST'])
@admin_endpoint
def api_create_patch_reference():
	try:
		title = get_value_or_blank(request, "title")
		shortdesc = get_value_or_blank(request, "shortdesc")
		fulldesc = get_value_or_blank(request, "fulldesc")
		forserver = get_value_or_blank(request, "forserver")
		server_id = get_value_or_blank(request, "fulldesc")
		Patch.AddUpdate(main_session, title, shortdesc, fulldesc, forserver, server_id)
		return "", 200
	except:
		return "There was an error adding that patch", 500
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
