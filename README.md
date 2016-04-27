#blueshed.micro
The problem is how to use Tornado with SqlAlchemy and scale.
The answer is python. Since python 3.4 there is a ProcessPoolExecutor class
which manages a pool of subprocess to which you can submit functions. All
your blocking requests are submitted to the pool, or you can have
multiple pools for fast and slow functions.

You can have multiple processes, schemas, databases, tornados... To have
websockets that broadcast state changes to their clients you'll need
a way of telling each tornado of the change. So a nice async service
is Pika. Tell Pika that each tornado should broadcast your change.

The micro websocket and handler pass a broadcast queue to the
subprocess in a context, and handle cookies and authentication that
way. The context returns unless an exception is raised. By using
annotations you can specify if your function requires a context.

Tornado is brilliant at server side templates and especially websockets.
SqlAlchemy is brilliant at complex, optimized sql driven by a domain
model. Python is brilliant because it enables both to be possible and
to work well together. pytest-tornado is another must have. It allows
you to test tornado application, even websockets, without coding anything
more complex that the hello world example on the tornadoweb.org index page. 

Still to come, memcache. MySQL is brilliant too as it provides
a memcache interface to inno_db tables. It means SqlAlchemy can mange you
cache within its transactions or schedule a persistent task for it to
be updated.

references:
* [tornado](http://www.tornadoweb.org/)
* [sqlalchemy](http://www.sqlalchemy.org/)
* [pika](http://pika.readthedocs.org/)
* [pytest-tornado](https://pypi.python.org/pypi/pytest-tornado)
* [innodb memcache](https://dev.mysql.com/doc/refman/5.6/en/innodb-memcached-setup.html)
	
Below are some sample projects that explore these ideas. They also include 
a NoSQL example.

# spddo-chat
heroku bound scalable chat
![alt tag](https://raw.githubusercontent.com/blueshed/spddo-chat/master/topology.png)

To run the chat example

	python -m spddo.chat.server


## spddo-micro
Now with a micro service framework.

To run the example micro:

	python -m spddo.micro.server



## spddo-mongo
There is also a demo of how to work with Motor and Mongodb using
fullCalendar's Scheduler.

To install you'll need brew:

	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
	
and to install mongodb:

	brew install mongodb
	
then you'll need to install the tornado mongo client:

	pip install motor
	
then to run:
	
	python -m spddo.mongo.server
	