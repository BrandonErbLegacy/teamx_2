from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import load_only
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from uuid import uuid4
from hashlib import sha256
import datetime
DatabaseBase = declarative_base()

class RecordExists(Exception):
	def __init__(self, message, field):

		# Call the base class constructor with the parameters it needs
		super(RecordExists, self).__init__(message)

		self.field = field

class User(DatabaseBase):
	__tablename__ = "Users"

	id = Column(String(36), primary_key=True)
	username = Column(String)
	password = Column(String)
	display_name = Column(String)
	first_name = Column(String)
	email = Column(String)
	salt = Column(String(36))
	date_registered = Column(DateTime(timezone=True), server_default=func.now())
	last_seen = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
	is_admin = Column(Boolean(), default=False) #Admin privs only
	is_superuser = Column(Boolean(), default=False) #All admin privs, plus can make admins

	def RegisterUser(session, username, password, display_name, first_name, email, ip):
		users_with_username = session.query(User).filter(User.username == username).first()
		if (users_with_username != None):
			raise RecordExists("", "username")

		users_with_email = session.query(User).filter(User.email == email).first()
		if (users_with_email != None):
			raise RecordExists("", "password")

		users_with_display_name = session.query(User).filter(User.display_name == display_name).first()
		if (users_with_display_name != None):
			raise RecordExists("", "display_name")

		user = User()
		user.id = new_uuid()
		user.salt = new_uuid()
		user.username = username
		user.password = sha256((user.salt+password).encode("utf-8")).hexdigest()
		user.display_name = display_name
		user.first_name = first_name
		user.email = email

		session.add(user)
		user_session = Session.CreateSession(session, user, ip)

		return (user, user_session.id)

	def UserExists(session, username):
		user = session.query(User).filter(User.username == username).first()
		return user

	def GiveAdmin(session, user_id):
		user = session.query(User).filter(User.id == user_id).first()
		if (user != None):
			user.is_admin = True
		else:
			return False
		session.commit()
		return True


	def LogUserIn(session, username, password, ip_addr):
		target_user = session.query(User).filter(User.username == username).first()
		if (target_user == None):
			return None
		hashed_password = sha256((target_user.salt+password).encode("utf-8")).hexdigest()
		if hashed_password == target_user.password:
			user_session = Session.CreateSession(session, target_user, ip_addr)
			return user_session
		else:
			return None

	def GetAdminUsers(session):
		users = session.query(User).filter(User.is_admin == 1).all()
		return users

	def GetAllUsers(session):
		all_users = session.query(User).all()
		#Manually converts to json. Can't do this for large numbers of results.
		#Will need to be changed eventually.
		json = "["
		for user in all_users:
			json = json + ('{"username":"%s", "display_name":"%s", "email":"%s", "last_seen":"%s"}, '%(user.username, user.display_name, user.email, user.last_seen))
		json = json[:-2] + "]"
		return json

	def UpdateUser(session, username, password, display_name, first_name, last_name, email):
		pass

class Session(DatabaseBase):
	__tablename__ = "Sessions"

	id = Column(String(36), primary_key=True)
	user_id = Column(String(36)) #User.id
	ip_address = Column(String(36))
	date_registered = Column(DateTime(timezone=True), server_default=func.now())
	is_expired = Column(Boolean(), default=False)
	#We'll use is_expired to do soft deletes of sessions (to allow tracking sessions)

	def CreateSession(session, user_object, ip_address):
		user_session = Session()
		user_session.id = new_uuid()
		user_session.user_id = user_object.id
		user_session.ip_address = ip_address

		session.add(user_session)

		session.commit()
		return user_session

	def ValidateSession(session, session_object, ip_address):
		pass

	def DeleteSession(session, session_object):
		pass

	def GetUserBySession(session, session_id_or_object):
		user_obj = None
		try:
			## Try to get the session_id by using session_id_or_object as a user object
			user_obj = session.query(User).filter(User.id == session_id_or_object.user_id).first()
		except:
			## Try to get the session by using the session_id_or_object as a session_id
			session_obj = session.query(Session).filter(Session.id == session_id_or_object).first()
			user_obj = session.query(User).filter(User.id == session_obj.user_id).first()
		if session_obj.is_expired:
			print("User attempted to use an expired token: "+user_obj.username)
			return None
		if session_obj.date_registered < datetime.datetime.now()-datetime.timedelta(hours=6):
			session_obj.is_expired = True
			session.commit()
			print("The user session has expired for: "+user_obj.username)
			return None
		else:
			return user_obj

class Server(DatabaseBase):
	__tablename__ = "Servers"

	id = Column(String(36), primary_key=True)
	name = Column(String)
	shortdesc = Column(String)
	fulldesc = Column(String)
	path_to_pic = Column(String)
	path_to_technic = Column(String)
	minecraft_version = Column(String)
	address = Column(String)

	def AddServer(session, name, path_to_pic, path_to_technic, minecraft_version, address, shortdesc, fulldesc):
		if session.query(Server).filter(Server.name == name).first() != None:
			raise RecordExists("", "name")
		server = Server()
		server.name = name
		server.path_to_pic = path_to_pic
		server.path_to_technic = path_to_technic
		server.minecraft_version = minecraft_version
		server.address = address
		server.shortdesc = shortdesc
		server.fulldesc = fulldesc
		server.id = new_uuid()

		session.add(server)
		session.commit()
		return server

	def GetById(session, id):
		return session.query(Server).filter(Server.id == id).first()

	def GetAll(session):
		return session.query(Server).all()

	def UpdateServer(session, name, path_to_pic, path_to_technic, minecraft_version):
		pass

	def FetchURL(self):
		return "/view_server/"+self.id

	def GetPlayerCount(self):
		return 0

	def GetMaxPlayers(self):
		return 20

	def GetTopThree(session):
		return session.query(Server).all()

	def GetMods(self, session):
		return Mod.GetModsByServer(session, self.id)

	def GetUpdates(self, session):
		return Update.GetUpdatesByServer(session, self.id)

class ServerPlayerMapping(DatabaseBase):
	__tablename__ = "MinecraftPlayers"
	id = Column(String(36), primary_key=True)
	minecraft_name = Column(String)
	minecraft_guid = Column(String(36))
	user_id = Column(String(36)) #User.id
	server_id = Column(String(36)) #User.id
	date_joined = Column(DateTime(timezone=True), server_default=func.now())

	def AddUserAccount(session, username, password, server_id, mc_guid):
		spm = session.query(ServerPlayerMapping).filter(ServerPlayerMapping.server_id == server_id).filter(ServerPLayerMapping.minecraft_guid == mc_guid).first()
		if spm != None:
			target_user = session.query(User).filter(User.username == username).first()
			if (target_user == None):
				return "No matching records found"
			hashed_password = sha256((target_user.salt+password).encode("utf-8")).hexdigest()
			if hashed_password == target_user.password:
				spm.user_id = target_user.id
				session.commit()
				return "Linking successful"
			else:
				return "No matching records found"
		else:
			return "There is no matching account"

class ServerActivityLog(DatabaseBase):
	__tablename__ = "ServerActivityLogs"
	id = Column(String(36), primary_key=True)
	action = Column(String)
	server_id = Column(String(36))
	server_player_mapping_id = Column(String(36)) #ServerPLayerMapping.id
	event_time = Column(DateTime(timezone=True), server_default=func.now())

	def AddServerActivityLog(session, action, server_id, player_id, player_name, generate_mapping=True):
		player_with_id = session.query(ServerPlayerMapping).filter(ServerPlayerMapping.minecraft_guid == player_id).filter(ServerPlayerMapping.server_id == server_id).first()
		if (generate_mapping):
			if (player_with_id != None):
				player_with_id.minecraft_name = player_name
				player_with_id.server_id = server_id
			else:
				player_with_id = ServerPlayerMapping()
				player_with_id.id = new_uuid()
				player_with_id.minecraft_name = player_name
				player_with_id.minecraft_guid = player_id
				player_with_id.server_id = server_id
				session.add(player_with_id)
		sal = ServerActivityLog()
		sal.id = new_uuid()
		sal.action = action
		sal.server_id = server_id
		if (generate_mapping):
			sal.server_player_mapping_id = player_with_id.id

		session.add(sal)
		session.commit()

	def ServerStarted(session, server_id):
		sal = ServerActivityLog()
		sal.id = new_uuid()
		sal.action = "SERVER_STARTED"
		sal.server_id = server_id

		session.add(sal)
		session.commit()

	def ServerStopped(session, server_id):
		sal = ServerActivityLog()
		sal.id = new_uuid()
		sal.action = "SERVER_PLANNED_STOPPED"
		sal.server_id = server_id

		session.add(sal)
		session.commit()

	def ServerCrashed(session, server_id):
		sal = ServerActivityLog()
		sal.action = "SERVER_CRASHED"
		sal.server_id = server_id

		session.add(sal)
		session.commit()

	def GetMaxPlayers(session, server_id):
		last_res = session.query(ServerActivityLog).filter(ServerActivityLog.server_id == server_id).order_by(ServerActivityLog.event_time.desc()).all()
		for sal in last_res:
			if ("PLAYER_MAX" in sal.action):
				return sal.action.split(":")[1]
		return str(20)

# Actions:
#  - PlayerLoggedOn
#  - PLayerLoggedOff
#  - PlayerKilledPLayer
#  - PLayerDied
#  - Server Started
#  - Server Quit
#  - Server Crashed

class Ticket(DatabaseBase):
	__tablename__ = "Tickets"
	id = Column(String(36), primary_key=True)
	title = Column(String)
	user_id = Column(String(36))
	server_id = Column(String(36)) #Server.id
	status = Column(String)
	date_created = Column(DateTime(timezone=True), server_default=func.now())

	def GetByUser(session, user):
		tickets = session.query(Ticket).filter(Ticket.user_id == user.id).filter(Ticket.status != "Closed").all()
		return tickets

	def GetRepliesByTicket(session, ticket):
		replies = session.query(TicketReply).filter(TicketReply.ticket_id == ticket.id).order_by(TicketReply.date_created.asc())
		return replies

	def GetTicketById(session, id, user):
		if (user != None):
			if (user.is_admin or user.is_superuser):
				ticket = session.query(Ticket).filter(Ticket.id == id).first()
			else:
				ticket = session.query(Ticket).filter(Ticket.id == id).filter(Ticket.user_id == user.id).first()
		else:
			ticket = session.query(Ticket).filter(Ticket.id == id).filter(Ticket.user_id == None).first()
		return ticket

	def OpenTicket(session, user, title, text, server_id):
		ticket = Ticket()
		ticket.id = new_uuid()
		ticket.title = title
		if (user != None):
			ticket.user_id = user.id
		else:
			ticket.user_id = None
		ticket.server_id = server_id
		ticket.status = "Open"

		ticket_reply = TicketReply()
		ticket_reply.id = new_uuid()
		ticket_reply.ticket_id = ticket.id
		if (user != None):
			ticket_reply.user_id = user.id
		else:
			ticket_reply.user_id = None
		ticket_reply.text = text

		session.add(ticket)
		session.add(ticket_reply)

		session.commit()
		return ticket

	def CommentTicket(session, ticket, user, text):
		ticket_reply = TicketReply()
		ticket_reply.id = new_uuid()
		ticket_reply.ticket_id = ticket.id
		if user != None:
			ticket_reply.user_id = user.id
		else:
			ticket_reply.user_id = None
		ticket_reply.text = text
		session.add(ticket_reply)
		session.commit()
		return ticket_reply

	def GetOpenTickets(session):
		tickets = session.query(Ticket).filter(Ticket.status != "Closed").all()
		return tickets

	def GetOpenCount(session):
		tickets = session.query(Ticket).filter(Ticket.status != "Closed").all()
		return len(tickets)

	def CloseTicket(session, ticket):
		ticket.status = "Closed"
		session.commit()
	#def AddReply(session, user, ticket):


class TicketReply(DatabaseBase):
	__tablename__ = "TicketReplies"
	id = Column(String(36), primary_key=True)
	ticket_id = Column(String(36)) #Ticket.id
	text = Column(String)
	user_id = Column(String(36)) #User.id
	date_created = Column(DateTime(timezone=True), server_default=func.now())

class Mod(DatabaseBase):
	__tablename__ = "Mods"
	id = Column(String(36), primary_key=True)
	name = Column(String)
	version = Column(String)
	source = Column(String)
	server_id = Column(String(36)) #User.id
	date_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

	def AddMod(session, name, version, server_id):
		server_object = session.query(Server).filter(Server.id == server_id).first()
		if server_object != None:
			mod = Mod()
			mod.name = name
			mod.version = version
			mod.server_id = server_object.id
			session.add(mod)
			session.commit()

	def EditListing(session, listing_id, version):
		listing = session.query(Mod).filter(Mod.id == listing_id).first()
		if (listing != None):
			listing.version = version
			session.commit()

	def RemoveListing(session, listing_id):
		listing = session.query(Mod).filter(Mod.id == listing_id).first()
		if (listing != None):
			session.remove(listing)
			session.commit()

	def GetModsByServer(session, server_id):
		return session.query(Mod).filter(Mod.server_id == server_id).all()

class Update(DatabaseBase):
	__tablename__ = "Updates"
	id = Column(String(36), primary_key=True)
	title = Column(String)
	version = Column(String)
	shortdesc = Column(String)
	fulldesc = Column(String)
	for_server = Column(Boolean(), default=False)
	server_id = Column(String(36)) #User.id
	date_created = Column(DateTime(timezone=True), server_default=func.now())
	date_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

	def AddUpdate(session, title, shortdesc, fulldesc, for_server, server_id):
		update = Update()
		update.title = title
		update.shortdesc = shortdesc
		update.fulldesc = fulldesc
		update.for_server = for_server
		update.server_id = server_id
		session.add(update)
		session.commit()

	def UpdateUpdate(session, update_id, title, shortdesc, fulldesc):
		update = session.query(Update).filter(Update.id == update_id).first()
		if (update != None):
			update.title = title
			update.shortdesc = shortdesc
			update.fulldesc = fulldesc
			session.commit()

	def DeleteUpdate(session, update_id):
		update = session.query(Update).filter(Update.id == update_id).first()
		if (update != None):
			session.remove(update)
			session.commit()

	def GetUpdatesByServer(session, server_id):
		return session.query(Update).filter(Update.server_id == server_id).all()

	def GetUpdatesForOther(session):
		return session.query(Update).filter(Update.for_server == False).all()











## Utility Functions ##
def new_uuid():
	return str(uuid4())










#################### End of File ######################
