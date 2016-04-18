'''
Created on 15 Apr 2016

@author: peterb
'''
from tornado import gen
from tornado.ioloop import IOLoop
from motor.motor_tornado import MotorClient
from spddo.mongo.control.context import Context
from spddo.mongo.control.login import login, AuthenticationException


Context.mongo_client = MotorClient('mongodb://localhost:27017')

@gen.coroutine
def do_login():
    context = Context("anon","1","login")
    user = None
    try:
        user = yield login(context, "pete@blueshed.co.uk", "daisya")
    except AuthenticationException:
        db = context.motor.zamazz_database
        yield db.users_collection.insert({'email': "pete@blueshed.co.uk", "password": "daisya" })
    
    if user is None:
        user = yield login(context, "pete@blueshed.co.uk", "daisya")
        assert user


# IOLoop.current().run_sync(do_insert)
IOLoop.current().run_sync(do_login)