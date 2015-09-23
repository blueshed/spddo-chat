'''
Created on 23 Sep 2015

@author: peterb
'''
from iron_mq import IronMQ
import os


class IronMQBroadcaster(object):
    
    def __init__(self, address):
        self._application = None
        mq = IronMQ(project_id=os.environ.get("IRON_MQ_PROJECT_ID"),
                    token=os.environ.get("IRON_MQ_TOKEN"))
        self.queue = mq.queue("broadcast_queue")
        self.queue.add_subscribers(address, push_type="multicast")
        
    def set_application(self, application):
        self._application = application
        
        
    def post(self, msg):
        self.queue.post(msg)