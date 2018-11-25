from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from threading import Thread
from flask import Flask, request, render_template
from hashlib import sha256
from uuid import uuid4

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
	return render_template('index.html', title='Home')

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
	return render_template('register.html', title='Register to become a user')

###############################
#####  Admin Site Routes  #####
###############################

@app.route('/admin')
def admin_login():
    return "Admin login or redirect"

###############################
#####   Rest API Routes   #####
###############################

DatabaseBase.metadata.create_all(db_engine)
main_session.commit()

app.run(debug=True)
