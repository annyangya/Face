from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
import os
from common.lib.UrlManager import UrlManager

class Application(Flask):
    def __init__(self, import_name, template_folder=None,root_path=None):
        super(Application, self).__init__(import_name,template_folder=template_folder, root_path=root_path,static_folder=None)
        self.config.from_pyfile('config/base_setting.py')

        if 'ops_config' in os.environ:
            self.config.from_pyfile('config/%s_setting.py' % (os.environ['ops_config']))

        db.init_app(self)

"""
export ops_config=local 

一般base是公用的，如端口号配置，数据库配置在local中
"""

db = SQLAlchemy()
app = Application(__name__,template_folder=os.getcwd()+"/web/templates/",root_path=os.getcwd())#当前目录+路径，也可直接将templates文件夹放在项目下
manager = Manager(app)
#app = Flask(__name__)

app.add_template_global(UrlManager.buildStaticUrl, "buildStaticUrl")
app.add_template_global(UrlManager.buildUrl, 'buildUrl')
