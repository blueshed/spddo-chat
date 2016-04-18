'''
Created on 15 Apr 2016

@author: peterb
'''
from tornado import gen
from tornado.ioloop import IOLoop
from motor.motor_tornado import MotorClient
import pprint


client = MotorClient('mongodb://localhost:27017')
db = client.test_database

@gen.coroutine
def do_insert():
    for i in range(2000):
        future = db.test_collection.insert({'i': i})
        result = yield future
        print(result)

@gen.coroutine        
def do_find_one():
    document = yield db.test_collection.find_one({'i': {'$lt': 1}})
    pprint.pprint(document)


# IOLoop.current().run_sync(do_insert)
IOLoop.current().run_sync(do_find_one)