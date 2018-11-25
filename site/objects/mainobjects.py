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

class Server(DatabaseBase):
    __tablename__ = "Servers"

    id = Column(String(36), primary_key=True)
    name = Column(String)
    path_to_pic = Column(String)
    path_to_technic = Column(String)
    minecraft_version = Column(String)

class ServerPlayerMapping(DatabaseBase):
    __tablename__ = "MinecraftPlayers"
    id = Column(String(36), primary_key=True)
    minecraft_name = Column(String)
    minecraft_guid = Column(String(36))
    user_id = Column(String(36)) #User.id
    server_id = Column(String(36)) #Server.id

class ServerActivityLog(DatabaseBase):
    __tablename__ = "ServerActivityLogs"
    id = Column(String(36), primary_key=True)
    action = Column(String)
	server_player_mapping_id = Column(String(36)) #ServerPLayerMapping.id
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

class Update(DatabaseBase):
    __tablename__ = "Updates"
    id = Column(String(36), primary_key=True)
	title = Column(String)
	desc = Column(String)
	for_server = Column(Boolean(), default=False)
	server_id = Column(String(36))























#################### End of File ######################
