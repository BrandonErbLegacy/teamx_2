# Welcome to the TeamX website repo
This is a flask based website. The purpose is to handle general community interaction and serve as a central point for syncing minecraft server related data.

# How to run
* Create a virtual environment using virtualenv
* Activate your virtualenv
* Use pip to install the requirements from requirements.txt
* Execute main.py

# How to create a local admin account
* Register for an account on your local site
* Open the database in something like SQLite Browser
* Change the is_admin field to be 1 (and optionally the is_superuser field to 1)
* Write the changes to the database and you're done
