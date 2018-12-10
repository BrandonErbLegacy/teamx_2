from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import load_only
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from uuid import uuid4
from hashlib import sha256
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
			user_obj = session.query(User).filter(User.id == session_id_or_object.user_id).first()
		except:
			session_obj = session.query(Session).filter(Session.id == session_id_or_object).first()
			user_obj = session.query(User).filter(User.id == session_obj.user_id).first()
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

class ServerPlayerMapping(DatabaseBase):
	__tablename__ = "MinecraftPlayers"
	id = Column(String(36), primary_key=True)
	minecraft_name = Column(String)
	minecraft_guid = Column(String(36))
	user_id = Column(String(36)) #User.id
	server_id = Column(String(36)) #User.id

	def AddServerPlayerMapping(session, minecraft_name, minecraft_guid, user_object, server_object):
		pass

	def UpdateServerPlayerMapping(session, server_player_mapping_object, server_object):
		pass

class ServerActivityLog(DatabaseBase):
	__tablename__ = "ServerActivityLogs"
	id = Column(String(36), primary_key=True)
	action = Column(String)
	server_player_mapping_id = Column(String(36)) #ServerPLayerMapping.id

	def AddServerActivityLog(session, action, server_player_mapping_object=None):
		pass
# Actions:
#  - PlayerLoggedOn
#  - PLayerLoggedOff
#  - PlayerKilledPLayer
#  - PLayerDied
#  - Server Started
#  - Server Quit
#  - Server Crashed

class Mod(DatabaseBase):
	__tablename__ = "Mods"
	id = Column(String(36), primary_key=True)
	name = Column(String)
	version = Column(String)
	server_id = Column(String(36)) #User.id
	def AddMod(name, version, server_object):
		pass

class Update(DatabaseBase):
	__tablename__ = "Updates"
	id = Column(String(36), primary_key=True)
	title = Column(String)
	desc = Column(String)
	for_server = Column(Boolean(), default=False)
	server_id = Column(String(36)) #User.id

	def AddUpdate(title, desc, for_server, server_object):
		pass

	def UpdateUpdate(update_object, title, desc):
		pass

	def DeleteUpdate(update_object):
		pass











## Utility Functions ##
def new_uuid():
	return str(uuid4())










#################### End of File ######################
