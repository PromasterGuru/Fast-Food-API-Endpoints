#app/__init__.py

"""
Initalize the app and load configurations
"""

from flask_api import FlaskAPI
from flask_restful import Api

#local imports
from instance.config import my_app_config
# from .api.v1.views import Login, Register, Orders, Order
#from .api.v2.database import DB
#from .api.v2.views import LoginV2, RegisterV2, OrdersV2, OrderV2

def create_app(app_config_name):
    """Wraps the creation of a new Flask object"""
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(my_app_config[app_config_name])
    app.config.from_pyfile('config.py')
    app_context = app.app_context()
    # app_context.push()
    # DB().init_db()

    api = Api(app, prefix="/api")

    api.add_resource(Login,
                    'auth/login'
                    )
    api.add_resource(Register,'/auth/signup')
    api.add_resource(Orders,'/orders/orders')
    api.add_resource(Order,'orders/<int:order_id>')

    return app
