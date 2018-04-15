#15 April 2018#
* There have been a couple of changes to the general structure. Firstly, I've
  added a script called the development scrip which you simply run on a unix
  machine and it lets you use Flask's development server and interactive
  debugger to debug and run your server, assuming your port 5000 is not
  occupied.
* Furthermore, in the database code, we have the ability to run a flask app
  command which resets the database and uses the ORM to map the models into
  database structures for you. Then you just import the database to fiddle
  with data and then commit it to the database when you're done. The model
  seems to be working well so far.
  Also, about to write a doc for starting up with the project and getting it
  running on Heroku etc.
  **ensure you've read the Heroku docs before you do anything else!!**

* Readme provisionally complete  (I'm sure there will be much more
  eventually!)