# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 14:10:59 2020

@author: czurm
"""
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.ext.automap import automap_base
import os, simplejson, logging
from dotenv import load_dotenv
load_dotenv()


#Init app
app = Flask(__name__)

#Database
POSTGRES = {
    'user': os.environ['DB_USER'],
    'pw':   os.environ['DB_PW'],
    'db':   os.environ['DB_NAME'],
    'host': os.environ['DB_HOST'],
    'port': '5432',
}


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%(user)s:\
%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_ECHO'] = True
#init db
db = SQLAlchemy(app)
Base = automap_base()
Base.prepare(db.engine, reflect=True)

#Acquire tables from db
Payment = Base.classes.payment
Rental  = Base.classes.rental
Inventory = Base.classes.inventory
Film = Base.classes.film


#init marshmallow
ma = Marshmallow(app)

class PaymentSchema(ma.Schema):
    class Meta:
        fields = ('payment_id', 'customer_id', 'staff_id', 'rental_id', 'amount', 'payment_date')
        model = Payment
        json_module = simplejson
        
class RentalSchema(ma.Schema):
    class Meta:
        fields = ('rental_id', 'rental_date', 'inventory_id', 'customer_id', 'return_date', 'staff_id', 'last_update')
        model = Rental

class FilmSchema(ma.Schema):
    class Meta:
        fields = ('film_id', 'title', 'description', 'release_year', 'language_id', 
                  'rental_duration', 'rental_rate', 'length', 'replacement_cost', 'rating', 
                  'last_update', 'special_features', 'fulltext')
        model = Film
        
class InventorySchema(ma.Schema):
    class Meta:
        fields = ('inventory_id', 'film_id', 'store_id', 'last_update')
        model = Inventory

#init schema
payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)

rental_schema = RentalSchema()
rentals_schema = RentalSchema(many=True)

film_schema = FilmSchema()
films_schema = FilmSchema(many=True)

inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)


"""
Display the most rented movies in descending order
"""
@app.route('/', methods=['GET'])
def index():
    q = db.session.query(Film.title, Film.description, Film.release_year, 
                         Film.length, Film.rating, db.func.count(Rental.inventory_id))\
                        .join(Inventory, Film.film_id == Inventory.film_id)\
                        .join(Rental, Inventory.inventory_id == Rental.inventory_id)\
                        .group_by(Film.film_id, Rental.inventory_id)\
                        .order_by(db.desc(db.func.count(Rental.inventory_id)))\
                        .all()
                        
    return render_template('index.html', rentals=q)

"""
payments api
"""
@app.route('/api/v1/resources/payments/all', methods=['GET'])
def all_payments():
    payments = db.session.query(Payment).all()
    result = payments_schema.dump(payments)
    return jsonify(result)

"""
rentals api
"""
@app.route('/api/v1/resources/rentals', methods=['GET'])
def rentals():
    query = db.session.query(Rental)
    
    #seek user parameters in URL
    query_parameters = request.args
    id_          = query_parameters.get('rentid')
    inventory_id = query_parameters.get('invid')
    customer_id  = query_parameters.get('custid')
    staff_id     = query_parameters.get('staffid')
    rental_date  = query_parameters.get('rentdate')
    return_date  = query_parameters.get('returndate')
    last_update  = query_parameters.get('lastupdate')
    
    
    filters = {}
       
    if(id_):
        filters['rental_id'] = id_
    if(inventory_id):
        filters['inventory_id'] = inventory_id
    if(customer_id):
        filters['customer_id'] = customer_id
    if(staff_id):
        filters['staff_id'] = staff_id
    if(rental_date):
        filters['rental_date'] = rental_date
    if(return_date):
        filters['return_date'] = return_date
    if(last_update):
        filters['last_update'] = last_update
    
    for attr in filters:
        query = query.filter(getattr(Rental, attr) == filters[attr])
    
    result = rentals_schema.dump(query.all())
    return jsonify(result)
    

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
