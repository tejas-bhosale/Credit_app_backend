import json
from logging import exception
from sys import implementation
import frappe
import inspect
import datetime
from pyparsing import ParseExpression
import requests
from sqlalchemy import true

import csv
import os
import credit_app.api_folder.controller.user as controllers

@frappe.whitelist()
def get_payload(payload):
    
    if payload.get('data'):
       
        if(isinstance(payload.get('data'),bytes)):
            payload['data'] = payload['data'].decode('utf-8')
        return json.loads(payload['data'])

    else:
        return payload


@frappe.whitelist()
def create_user(**kargs):

    user_jason = get_payload(kargs)
    return controllers.create_user(user_jason)


@frappe.whitelist()
def login_user(**kargs):

    login_user = get_payload(kargs)
    return controllers.login_user(login_user)

@frappe.whitelist()
def request_amount(**kargs):

    request_amount = get_payload(kargs)
    return controllers.request_amount(request_amount)

@frappe.whitelist()
def get_all_borrow_request():

    # request_amount = get_payload(kargs)
    return controllers.get_all_borrow_request()


@frappe.whitelist()
def pay_borrower(**kargs):

    data = get_payload(kargs)
    return controllers.pay_borrower(data)

@frappe.whitelist()
def get_user_info(email):

    # data = get_payload(kargs)
    return controllers.get_user_info(email)

@frappe.whitelist()
def get_lenders_info(email):

    # data = get_payload(kargs)
    return controllers.get_lenders_info(email)

@frappe.whitelist()
def pay_lender(**kargs):

    data = get_payload(kargs)
    return controllers.pay_lender(data)

@frappe.whitelist()
def add_amount(**kargs):

    data = get_payload(kargs)
    return controllers.add_amount(data)

@frappe.whitelist()
def get_total_lending(email):

    # data = get_payload(kargs)
    return controllers.get_total_lending(email)






