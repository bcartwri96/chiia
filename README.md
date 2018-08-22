**IMPORTANT NEW THINGS TO DO!**
1. Github is now where our code is being pulled and pushed from; add it as a
   remote branch `git remote add HTTPS/SSH link here`
2. Download the Zenhub extension and then ensure it works by checking the
   Zenhub tab in our new Github repo
3. Let Ben know if you run into _any_ trouble :) 

DEV Docs
=========
1) **REALLY IMPORTANT FIRST STEP: checkout the dev_master branch of the project (explained below); for the git noobs (like me...): `git checkout dev_master`**
2) dev_master is our main branch where we do any and all development; PLEASE don't push to the master branch, because the master branch is also production
   which means it's linked to our heroku web app and so we're all ready to ship production code that's when we do the merge and resolve conflicts
3) You **need** to be reasonably familiar with Heroku, Jinja2, Flask, gunicorn, WSGI, Python, something called the Process Model (see Heroku docs) and
   the MVC (model view controller) method. Check them all out; a simple Google search will fill you in!
4) Before you run any code using `heroku local dev` you'll need to set environment variables. On a mac/linux machine, just run `source enviro_vars.sh` to
   do so!

An Important Note about Security
========
So you'll notice in enviro_vars.sh the first line contains an environment variable called secret key. This is a base64 encoded, operating system generated 24 character seed random variable I've produced, but we shouldn't all use the same environment variables. Instead, find out how your OS does it and then use theirs (it'll be more secure than anything you or I could mock up!)
For mac users, it's really easy. Here it is in python:
`python` (get into the shell); `import os`; `print(os.urandom(48))` and you've got it! Copy the value into the enviro script (replacing my one) before you start out and then you'll be fine. Do it wrong, and it'll screw up the secure sessions packages and code I've got running in the backend.

For those who want to see this working but don't know what quite to do (this was me...)
========
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

What do all these files even do?
==================================
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


How does this all work?
==========================
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

But where does Heroku come in?
==============================
Another good question! Heroku is the Paas (platform as a service) we'll use to host the production code and manage our database/web server. We don't actually
have to interact with Heroku too much, but when we do it'll be important that we do it right! Most of the time you'll notice it because we
``git push heroku dev_master`` instead of just `git push` because Heroku is set up as a 'git remote' which means when we push we need to tell it where to go
because it'll assume `origin master` by default, which doesn't actually exist!
Other than that we'll interact with Heroku whenever we want to push to our production branch, which we should probably do as a team so we don't break things!
That's really it. Heroku is our web server, essentially. We'll also be asking Susan to foot the bill for when we get the server going properly (at the moment
it's on a hobby plan) which is fine for what we're currently doing, but I don't think Susan will want to wait ~20 seconds for her webpage to load normally!
After a little while of inactivity on a heroku hobby plan, the webserver dyno (remember a dyno is an abstraction of a web service like an apache server etc.)
will simply go to sleep and when a user interupts that with a request, it can take some time to get started again!
=======
# CHIIA-DB

## CHIIA DATABASE WORKFORCE STRUCTURE

### About our Project:
**The Chinese Investment in Australia (CHIIA) Database** is a public database of Mainland Chinese direct commercial investment in Australia. The CHIIA database publishes a detailed dataset of individual commercial transactions of all sizes, which aligns with complementary data from the Australian Bureau of Statistics and the American Enterprise Institute’s Global Investment Tracker. The CHIIA methodology produces data from transparent sources, using consistent classifications and methods, making it suitable for use in peer-reviewed academic publications. The CHIIA methodology is published online to inform those who use this data and allow our colleagues around the world to create similar databases for their country. The CHIIA database was created, and is maintained by the East Asian Bureau of Economic Research at the Crawford School of Public Policy at The Australian National University.

### Team:

| Name        | Uni id       |
| ------------- |:-------------:|
| Anurag Vijay Kumar     | u6320283|
| Ao Sun     | u6126510     |   
| Benjamin Cartwright  | u5838255      |
| Nidhi Chaudhary   | u6281543     |
| Rajkamal Dhull  |u6345375     |




To view more about this project, please proceed to our [Landing Page.](https://sites.google.com/s/1wjU4dPP7f6Wb2QxUPzAfJoV6wSTdz2Ts/p/1NkN570w5u3MzU_j_zp-6VNILJb1qo1dS/edit?authuser=2)
