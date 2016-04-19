
class BaseContext:
    '''
        Stateful context that can be passed as an argument to function
        by annotating the argument with :micro-context
    '''
        
    def __init__(self, client_id, action_id, action, cookies=None):
        self.client_id = client_id
        self.action_id = action_id
        self.action = action
        self.cookies = cookies if cookies else {}
        self.broadcasts = []
    
    def broadcast(self, signal, message):
        self.broadcasts.append((signal,message))
        
    def set_cookie(self, key, value=None):
        if value is None:
            if key in self.cookies:
                del self.cookies[key]
        else:
            self.cookies[key]=value
            
    def get_cookie(self, key, default=None):
        return self.cookies.get(key, default)