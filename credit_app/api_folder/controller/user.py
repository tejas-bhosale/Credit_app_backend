from dataclasses import fields
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
from werkzeug.wrappers import Response
from frappe.utils.response import json_handler

def generate_response(status, msg, data=None):
    # frappe.errprint(data)
    response = Response()
    data = {
        "status"  : status,
        "message" : msg,
        "data"    : data
    }
    response.mimetype = 'application/json'
    response.charset = 'utf-8'
    response.data = json.dumps(data, default=json_handler,separators=(',',':'))
    return response

def object_mapper(json_input, object):
    for key in json_input.keys():
        if type(json_input[key]) is list:
            for item in json_input[key]:
                object.append(key, item)
        else:
            setattr(object, key, json_input[key])
    return object


def create_user(user_data):

    # user_data.pop('password', None)
    user_data.pop('re_password', None)
    user_data['name'] = user_data.get('email_id')

    user_doc = frappe.new_doc('Users')
    object_mapper(user_data,user_doc)
    user_doc.save()

    frappe.db.commit()


    return  generate_response('green','User Created',user_data)


def login_user(login_data):
    print("login_data",login_data)

    # user_doc = frappe.get_doc("Users",{"email_id":login_data.get('email'),"password":login_data.get('password')})
    try:
        user_doc = frappe.get_doc("Users",{"email_id":login_data.get('email'),"password":login_data.get('password')})
    except Exception as e:
        user_doc = None
    
    if user_doc is None:
        return generate_response('red','User Not Present',login_data)
 
    return generate_response('green','User Loggedin',user_doc)


def request_amount(request_data):
    try:
        # transaction_doc = frappe.doc("Transactions",{"amount":request_data.get('amount'),"duration":request_data.get('duration'),"requested_date":req})
        transaction_doc = frappe.new_doc("Transactions")
    except Exception as e:
        return generate_response('red','Request Not created',e)
        

    object_mapper(request_data,transaction_doc)
    transaction_doc.status = "Requested"
    transaction_doc.save()
    frappe.db.commit()

    return generate_response('green','Borrow request created',transaction_doc)

def get_all_borrow_request():
    borrow_list = frappe.get_list("Transactions",fields=["*"] ,filters={"status":"Requested"})

    if borrow_list is None:
        return generate_response('red','Borrow list not found')
    
    return generate_response('green','Borrow list returned',borrow_list)

def pay_borrower(data):

    try:
        transaction_doc = frappe.get_doc("Transactions",{"name":data.get('name')})
    except Exception as e:
        return generate_response('red','Error occured',e)
    
    object_mapper(data,transaction_doc)
    transaction_doc.status = "Borrowed"
    transaction_doc.save()

    try:
        lender_doc = frappe.get_doc("Users",{"email_id":data.get('lender_email')})
    except Exception as e:
        return generate_response('red','Error occured',e)
    
    if(int(lender_doc.balance) >int(transaction_doc.amount)):
        lender_doc.balance = int(lender_doc.balance) - int(transaction_doc.amount)
    else:
        return generate_response('red',"You don't have enogh balance",e)
    

    lender_doc.save()

    try:
        borrower_doc = frappe.get_doc("Users",{"email_id":transaction_doc.borrower_email})
    except Exception as e:
        return generate_response('red','Error occured',e)
    
    borrower_doc.balance = int(borrower_doc.balance) + int(transaction_doc.amount)
    borrower_doc.credit = int(borrower_doc.credit) + int(transaction_doc.amount)

    borrower_doc.save()

    frappe.db.commit()

    return generate_response('green','Transaction successfuly complete',transaction_doc)


def get_user_info(email):
    try:
        user_doc = frappe.get_doc("Users",{"email_id":email})
    except Exception as e:
        return generate_response('red','User not found',e)
    
    return generate_response('green',"User Returned",user_doc)

def get_lenders_info(email):
    try:
        lender_list = frappe.get_list("Transactions",fields=["*"] ,filters={"status":"Borrowed","borrower_email":email})
    except Exception as e:
        return generate_response('red','Lender list not found',e)
    
    return generate_response('green','Lender list returned',lender_list)

def pay_lender(data):

    try:
        transaction_doc = frappe.get_doc("Transactions",{"name":data.get('name')})
    except Exception as e:
        return generate_response('red','Error occured',e)
    
    transaction_doc.status = "Returned"
    transaction_doc.returned_date = data.get('returned_date')
    
    try:
        borrower_doc = frappe.get_doc("Users",{"email_id":transaction_doc.borrower_email})
    except Exception as e:
        return generate_response('red','Error occured',e)
    
    if int(borrower_doc.balance) > int(transaction_doc.amount):
        borrower_doc.balance = int(borrower_doc.balance) - int(transaction_doc.amount)
        borrower_doc.credit = int(borrower_doc.credit) - int(transaction_doc.amount)
    else:
        return generate_response('red',"You don't have enough balance")
    
    try:
        lender_doc = frappe.get_doc("Users",{"email_id":transaction_doc.lender_email})
    except Exception as e:
        return generate_response('red','Error occured',e)
    
    lender_doc.balance = int(lender_doc.balance) + int(transaction_doc.amount)

    transaction_doc.save()
    borrower_doc.save()
    lender_doc.save()
    frappe.db.commit()

    return generate_response('green','Amount Paid to lender',transaction_doc)


def add_amount(data):

    try:
        user_doc = frappe.get_doc("Users",{"email_id":data.get('email_id')})
    except Exception as e:
        return generate_response('red','User not found',e)
    
    if user_doc.balance == "" or user_doc.balance  == " ":
        user_doc.balance = 0
    
    user_doc.balance = int(user_doc.balance) +  int(data.get('amount'))

    user_doc.save()
    frappe.db.commit()

    return generate_response('green','Balance added',user_doc)

def get_total_lending(email):
    borrow_list = frappe.get_list("Transactions",fields=["*"] ,filters={"status":"Borrowed","lender_email":email})

    total_lending_amount = 0

    for i in range(len(borrow_list)):
        total_lending_amount += int(borrow_list[i]['amount'])

    print("############borrow_list##################",borrow_list)
    return generate_response('green','Total lending amount returned',total_lending_amount)


    pass

   








        
        

