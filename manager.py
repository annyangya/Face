from application import app, manager
from flask_script import Server
import www
import socket
hostname = socket.gethostname()
ip = socket.gethostbyname(hostname)
print(ip)

#自定义命令
manager.add_command("runserver", Server(host='10.137.31.232',port=app.config['SERVER_PORT'],use_debugger=True,use_reloader=None))

def main():
    manager.run()

if __name__ == '__main__':
    try:
        import sys
        sys.exit(main())
    except Exception as e:
        import traceback
        traceback.print_exc(e)