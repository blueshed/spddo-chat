from micro.utils.orm_utils import connect
import logging

_session_ = None
_engine_ = None

def db_init(db_url, db_echo=False, db_pool_recycle=None):
    global _session_, _engine_
    _engine_, _session_ = connect(db_url, db_echo, db_pool_recycle)
    logging.info("connecting to: %s", db_url)
    
    
def session():
    ''' returns a self closing session for use by with statements '''
    global _session_
    session = _session_()

    class closing_session:

        def __enter__(self):
            return session

        def __exit__(self, type_, value_, traceback_):
            session.close()
            
    return closing_session()