# spddo-chat
heroku bound scalable chat
![alt tag](https://raw.githubusercontent.com/blueshed/spddo-chat/master/topology.png)

To run the chat example

	python -m spddo.chat.server


## spddo-micro
Now with a micro service framework.

To run the example micro:

	python -m spddo.micro.server
	
NB: blueshed.micro is now a library and the examples
show how to use it. More documentation on the way.


## spddo-couch
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
	