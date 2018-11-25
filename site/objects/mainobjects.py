from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import load_only
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
DatabaseBase = declarative_base()

class User(DatabaseBase):
    __tablename__ = "Users"

    id = Column(String(36), primary_key=True)
    username = Column(String)
    password = Column(String)
    display_name = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    salt = Column(String(36))
    date_registered = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), onupdate=func.now())
    is_admin = Column(Boolean(), default=False) #Admin privs only
    is_superuser = Column(Boolean(), default=False) #All admin privs, plus can make admins

	def RegisterUser(username, password, display_name, first_name, last_name, email):
		pass

	def LogUserIn(username, password):
		pass

	def UpdateUser(username, password, display_name, first_name, last_name, email):
		pass

class Session(Data)
    __tablename__ = "Users"

    id = Column(String(36), primary_key=True)
	user_id = Column(String(36) #User.id
	#expiration_date =

	def CreateSession(user_object, ip_address):
		pass

	def ValidateSession(session_object, ip_address):
		pass

	def DeleteSession(session_object):
		pass

	def GetUserBySession(session_object):
		pass

class Server(DatabaseBase):
    __tablename__ = "Servers"

    id = Column(String(36), primary_key=True)
    name = Column(String)
    path_to_pic = Column(String)
    path_to_technic = Column(String)
    minecraft_version = Column(String)

	def AddServer(name, path_to_pic, path_to_technic, minecraft_version):
		pass

	def UpdateServer(name, path_to_pic, path_to_technic, minecraft_version):
		pass

class ServerPlayerMapping(DatabaseBase):
    __tablename__ = "MinecraftPlayers"
    id = Column(String(36), primary_key=True)
    minecraft_name = Column(String)
    minecraft_guid = Column(String(36))
    user_id = Column(String(36)) #User.id
    server_id = Column(String(36)) #Server.id

	def AddServerPlayerMapping(minecraft_name, minecraft_guid, user_object, server_object):
		pass

	def UpdateServerPlayerMapping(server_player_mapping_object, server_object):
		pass

class ServerActivityLog(DatabaseBase):
    __tablename__ = "ServerActivityLogs"
    id = Column(String(36), primary_key=True)
    action = Column(String)
	server_player_mapping_id = Column(String(36)) #ServerPLayerMapping.id

	def AddServerActivityLog(action, server_player_mapping_object=None):
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
	server_id = Column(String(36))
	def AddMod(name, version, server_object):
		pass

class Update(DatabaseBase):
    __tablename__ = "Updates"
    id = Column(String(36), primary_key=True)
	title = Column(String)
	desc = Column(String)
	for_server = Column(Boolean(), default=False)
	server_id = Column(String(36))

	def AddUpdate(title, desc, for_server, server_object):
		pass

	def UpdateUpdate(update_object, title, desc):
		pass

	def DeleteUpdate(update_object):
		pass






















#################### End of File ######################
