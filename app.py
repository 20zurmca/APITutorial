# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 14:10:59 2020

@author: czurm
"""
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.ext.automap import automap_base
import os, simplejson
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
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #do a simple test? Check this out
#init db
db = SQLAlchemy(app)
Base = automap_base()
Base.prepare(db.engine, reflect=True)

#Acquire tables from db
Payment = Base.classes.payment

#init marshmallow
ma = Marshmallow(app)

class PaymentSchema(ma.Schema):
    class Meta:
        fields = ('payment_id', 'customer_id', 'staff_id', 'rental_id', 'amount', 'payment_date')
        model = Payment
        json_module = simplejson

#init schema
payment_schema = PaymentSchema()
payments_schema = PaymentSchema(many=True)


@app.route('/payments', methods=['GET'])
def get():
    all_payments = db.session.query(Payment).all()
    result = payments_schema.dump(all_payments)
    return jsonify(result)

# Run Server
if __name__ == '__main__':
    app.run(debug=True)
