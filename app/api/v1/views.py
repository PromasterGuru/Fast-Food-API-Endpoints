#app/api/v1/views.py

'''
Implementation of API EndPoint
'''
import re
import datetime
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify, request, abort
from flask_restful import Resource


#local import
from .models import FoodOrders


class Register(Resource):
    """Resigsters new users"""


    users = FoodOrders()

    def post(self):
        '''Register new users'''
        if (not request.json
                or not "username" in request.json
                or not "password" in request.json
           ):
            result = {"Message": "Invalid username or password"}
            response = jsonify(result)
            response.status_code = 400 #Bad request
        else:
            uname = request.json['username']
            password = request.json['password']
            if not uname:
                result = {"Message": "Please enter your username!!"}
                response = jsonify(result)
                response.status_code = 400 #Bad request
            elif len(uname) < 6:
                result = {"Message": "Username must contain atleast 6 characters!!"}
                response = jsonify(result)
                response.status_code = 400 #Bad request
            elif not password:
                result = {"Message": "Please enter your password!!"}
                response = jsonify(result)
                response.status_code = 400 #Bad request
            elif len(password) < 8:
                result = {"Message": "password must have more than 8 characters!!"}
                response = jsonify(result)
                response.status_code = 400 #Bad request
            elif re.search('[0-9]', password) is None:
                result = {"Message": "password must contain a atleast one number!!"}
                response = jsonify(result)
                response.status_code = 400 #Bad request
            elif re.search('[A-Z]', password) is None:
                result = {"Message": "password must contain a capital letter!!"}
                response = jsonify(result)
                response.status_code = 400 #Bad request
            elif uname in self.users.get_users():
                result = {"Message": "Username is already registered, please login"}
                response = jsonify(result)
                response.status_code = 401 #An authorized
            else:
                password_hash = generate_password_hash(password, method='sha256')
                self.users.set_users(uname, password_hash)
                result = {"Message":"You have successfully registered as "+uname}
                response = jsonify(result)
                response.status_code = 201 #Created
        return response


class Login(Register):
    '''Authenticates users'''


    def get(self):
        '''Login'''
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            result = {"Message": "User not verified, Please login!"}
            response = jsonify(result)
            response.status_code = 401 #OK
        else:
            if auth.username not in self.users.get_users():
                result = {"Message": "Username not registered, please register!!!"}
                response = jsonify(result)
                response.status_code = 401  #An authorized
            else:
                uname = auth.username
                if check_password_hash(self.users.get_users()[uname],auth.password):
                    token = jwt.encode({'username': uname,
                                        'exp': datetime.datetime.utcnow()
                                        + datetime.timedelta(minutes=15)
                                        },app.config['SECRET_KEY'])
                    result = {"Message": "Login successful, Welcome %s"%(uname),
                              "Token": token.decode('UTF-8')}
                    response = jsonify(result)
                    response.status_code = 200 #OK
                else:
                    result = {"Message": "Username or password was incorrect!"}
                    response = jsonify(result)
                    response.status_code = 401 #An authorized
        return response

class Orders(Resource):
    """Class that holds the API endpoints that deals with multiple orders"""


    orders = FoodOrders()


    def get(self):
        '''Get all the orders.'''
        order = self.orders.get_orders()
        if order:
            result = {"Message": self.orders.get_orders()}
            response = jsonify(result)
            response.status_code = 200 #OK
        else:
            result = {"Message": "No orders found"}
            response = jsonify(result)
            response.status_code = 404 #OK
        return response

    def post(self):
        '''Place a new order'''
        if not request.json or not "order_item" in request.json:
            result = {"Message": "Unknown request!!"}
            response = jsonify(result)
            response.status_code = 400 #Bad request
        else:
            item = request.json['order_item']
            desc = request.json['description']
            order = [order for order in self.orders.get_orders()
                     if(
                         order['order_item'] == item and
                         order['description'] == desc
                         )
                     ]
            if not order:
                if not self.orders.get_orders():
                    order_id = 1
                else:
                    order_id = self.orders.get_orders()[-1]['id'] + 1
                new_order = {
                    "id": order_id,
                    "order_item": item,
                    "description": desc,
                    "quantity": request.json['quantity'],
                    "order_date": str(datetime.datetime.now())[:19],
                    "status": "Pedding"
                }
                self.orders.set_orders(new_order)
                result = {"Message": new_order}
                response = jsonify(result)
                response.status_code = 201 #Created
            else:
                result = {"Message": "Dublicate orders not allowed!!"}
                response = jsonify(result)
                response.status_code = 400 #Bad request
        return response


class Order(Orders):
    '''Holds API endpoints with specific orders'''


    food_orders = Orders.orders.get_orders()

    def validate(self, order_id):
        """Ensure user enters a valid order"""
        if len(self.orders.get_orders()) < order_id:
            return True

    def check_order(self, order_id):
        """Get user request"""
        order = [order for order in self.orders.get_orders()
                 if order['id'] == order_id
                 ]
        return order

    def get(self, order_id):
        '''Fetch a specific order'''
        if self.validate(order_id):
            result = {"Message": "No order found for id %d" %(order_id)}
            response = jsonify(result)
            response.status_code = 404 #Not found
        else:
            order = self.check_order(order_id)
            result = {"Message": order}
            response = jsonify(result)
            response.status_code = 200 #OK
        return response

    def put(self, order_id):
        '''Update the status of an order'''
        if self.validate(order_id):
            result = {"Message": "No order found for id %d" %(order_id)}
            response = jsonify(result)
            response.status_code = 404 #Not found
        else:
            order = self.check_order(order_id)
            order[0]['status'] = request.json['status']
            result = {"Message": order}
            response = jsonify(result)
            response.status_code = 200 #OK
        return response

    def delete(self, order_id):
        '''Delete an order'''
        if self.validate(order_id):
            result = {"Message": "No order found for id %d" %(order_id)}
            response = jsonify(result)
            response.status_code = 404 #Not found
        else:
            self.food_orders.remove(self.check_order(order_id)[0])
            result = {"Message": "Order deleted successfully"}
            response = jsonify(result)
            response.status_code = 200 #OK
        return response
