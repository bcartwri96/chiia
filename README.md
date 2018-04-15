#DEV DOCS#

##Important Info##
1) dev_master is our main branch where we do any and all development; PLEASE don't push to the master branch, because the master branch is also production
   which means it's linked to our heroku web app and so we're all ready to ship production code that's when we do the merge and resolve conflicts
2) You **need** to be reasonably familiar with Heroku, Jinja2, Flask, gunicorn, WSGI, Python, something called the Process Model (see Heroku docs) and
   the MVC (model view controller) method. Check them all out; a simple Google search will fill you in!


##For those who want to see this working but don't know what quite to do (this was me...)##
_disclaimer: this is only for Mac and Linux users; if you're on Windows, this is harder because Windows isn't built with bash/Python/scripting languages in
general in mind..._
1) Download Heroku CLI
2) Check out pipenv (for Python) (you can get it using Python's package manager PIP; `pip install heroku-cli`) and then set up a folder in the right spot on
   your machine and then create a virtual environment (pipenv tutorial; follow it!) *ensure you've specifiec the python installation should be Python 3*
3) Start your virtual env. 
4) `heroku login` and authenticate (i'll need to add you as a Heroku developer after this so just message me and I'll do that)
5) Then, because Heroku is cool, you can get the entire repo history, every branch, create the directory it's supposed to live in, and everything you'll 
   need for local Heroku dev using `heroku git:clone -a chia-db`
6) Wait for this to clone and then there should be a requirements.txt file in the root, so simply `pip install -r requirements.txt` and it should 
   pull all the right versions of all the libraries you'll need to execute the project locally. (that might take a minute...)
7) Download and install Postgres (it's a high level database tool)
8) You'll need to set some environment variables (*lerarn what they are and how they work on your OS!!*); do this by running the enviro_vars.sh script
   (`sh enviro_vars.sh`) *BUT be sure to modify the settigs inside so they work for your machine. In pacticular, the user who owns the postgres server 
   won't be _bencartwright_ like it says!*
9) Then check all this by jumping into the Python shell (`python3` or `python` (depending on which way your venv installs python)) and then cd into the 
   code directory and run `python`; `import datbase as db` ; `db.resetdb()` and it should import the models and use the SQL ORM to create the database 
   correctly.
10) Then you should be all good to run `heroku local web` and it'll look in the Procfile (in root dir) (which you know about because you read the docs;) )
    and it runs the command mapped by "web: long bash command here" or, if you want the developemnt server, run `heroku local dev`

##What do all these files even do?##
Well, good question!
Below I enumerate a dictionary mapping the name of the file or directory and the semantics.
| Name | Meaning |
| --- | --- |
| Procfile | Contains the mappings between `heroku local _something_` and the actual command which be is being executed on you local machine
| code/ | This directory contains all the source code  |
| requirements.txt | Contains the list of libraries which the project needs in order to execute! `pip install -r requirements.txt ` installs them  |
| enviro_vars.sh  | file contains the list of environment variables which *absolutely* must be set in order for the development server to connect to the db |
| config.py | Important for some reason so Flask knows what's happnening with the python modules etc. (?) |
| readme.md  | this file. |


##How does this all work?##
The basics are:
1) When a user requests a site, they are first sent to the main.py file in ~/code and in there you'll notice the app checks what their URL is and links them 
   the appropriate controller function.
2) The controller function now has exact control over the what the user receives, and this is dictated by the controller function which was referenced.
   We then do the necessary database connections (after importing the databae file) and then we serve them the appropriate template, passing it the necessary
   information for it to work correctly.
3) Note that the controller will use flask (imported as `fl` by convention) to `render_template` which means it parses the html file we write and adds in 
   anything we tell it to using the syntactic markup language (with conditionals and loops built-in!) defined in Jinja2 (the markup lang.)
4) Then the site is served to the user.


Got the basics? Cool :)
