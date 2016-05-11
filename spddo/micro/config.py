from tornado.options import define
from blueshed.micro.utils.config import load_config  # @UnusedImport

define('DEBUG',
       default=False,
       type=bool,
       help='run in debug mode')

define('PORT',
       default=8080,
       type=int,
       help='port to listen on')

define("CLEARDB_DATABASE_URL",
       default='mysql://root:root@localhost:8889/test',
       help="database url")

define("DB_POOL_RECYCLE",
       default=60,
       type=int,
       help="how many seconds to recycle db connection")

define("PROC_POOL_SIZE",
       default=0,
       type=int,
       help="how processes in the pool")

define("CLOUDAMQP_URL",
       default="",
       help="rabbitmq url for broadcasting")

define("CORS_URLS",
       default=["http://localhost:8080", 
                "http://petermac.local:8080",
                "https://spddo-chat.herokuapp.com"],
       multiple=True,
       help="access from where")

define("WS_URL",
       default="",
       help="restict connection from single source")

define("LOG_FORMAT",
       default="[%(levelname)1.1s %(asctime)s %(process)d %(thread)x  %(module)s:%(lineno)d] %(message)s",
       help="log format, default with process id")
