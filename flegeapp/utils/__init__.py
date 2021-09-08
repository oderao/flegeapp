import frappe
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs


@frappe.whitelist(allow_guest=True)
def create_flege_app(**args):
    try:
        patient = create_patient(**args)
        if patient:
            create_subscription(patient)
            create_delivery_note()
    except:
        frappe.local.response['http_status_code'] = 400
        frappe.local.response['message'] = 'Invalid request'

@frappe.whitelist()
def create_patient(**args):
    ''' Create Patient from data sent from front end '''
    try:
        #use frappe.request.data as workaround:- v13 convert list values in dict value inappropriately 
        
        if frappe.request.data :
            args = json.loads(frappe.request.data)
        if args:
            #convert dict to object
            args = frappe._dict(args)
            care_box_items = []
            order_table = []

            #create care box table
            for box_item in args.care_box:
                box = frappe.get_doc({
                    'doctype':'Care Box',
                    'item':box_item['item'],
                    'quantity':box_item['quantity'],
                    'size':box_item['size']
                })
                care_box_items.append(box)

            pflege_order = create_pflege_order(**args)
            if pflege_order:
                order = frappe.get_doc({
                                'doctype':'Patient Order Table',
                                'sales_order':pflege_order.name,
                                'date':pflege_order.transaction_date
                })
                order_table.append(order)

            patient = frappe.get_doc({
                'doctype':'Pflege Patient',
                'title':args.title,
                'first_name':args.first_name,
                'last_name':args.last_name,
                'street_name':args.street_name,
                'date_of_birth':args.date_of_birth,
                'zip_code':args.zip_code,
                'country':args.country,
                'care_level':args.care_level,
                'care_box':care_box_items,
                'order_table':order_table,
                'phone_number':args.phone_number,
                'email_address':args.email_address,
                'insurance_company':args.insurance_company,
                'insurance_number':args.insurance_number,
                'year':args.year,
                'note':args.note
            })
            patient.save()
            frappe.db.commit()
            if patient:
                frappe.local.response['http_status_code'] = 200
                frappe.local.response['message'] = 'patient created successfully'
                frappe.local.response['data'] = {'patient_id':patient.name}
    except:
        frappe.log_error(frappe.get_traceback(),'create_patient')
        frappe.local.response['http_status_code'] = 400
        frappe.local.response['message'] = 'Invalid request,-invalid data sent'

def create_pflege_order(**args):
    ''' create sales order from patient order '''
    args = frappe._dict(args)
    try:
        customer_name = args.first_name + ' ' + args.last_name
        
        #check if customer is already existing:
        if frappe.db.exists('Customer',customer_name):
            customer = frappe.db.get_value('Customer',customer_name,'name')
        else:
            customer = frappe.new_doc('Customer')
            customer_name = customer_name
            customer_group = 'Patient Group'
            customer_type = 'Individual'
            customer.save()
        items = []
        for i in args.care_box:
            item = frappe.get_doc({
                'doctype':'Sales Order Item',
                'item_code':i['item'],
                'delivery_date':frappe.utils.getdate(),
                'qty':i['quantity']
            })
            items.append(item)
        sales_order = frappe.get_doc({
            'doctype':'Sales Order',
            'customer':customer,
            'items':items
        })
        sales_order.insert(ignore_permissions=True)
        return sales_order
    except Exception as e:
        frappe.log_error(frappe.get_traceback(),'sales_order_creation_failed')

@frappe.whitelist()
def update_patient(**args):
    """ this handles the update of patient care box only"""
    url = frappe.request.url
    parsed_url = urlparse(url)
    query_dict = parse_qs(parsed_url.query)
    if query_dict and not query_dict.get('patient_id'):
        frappe.local.response['http_status_code'] = 400
        frappe.local.response['message'] = 'patient_id not in query'
    if query_dict and query_dict.get('patient_id'):
        #check if patient ID exists in the database
        patient_id = query_dict['patient_id'][0]
        if frappe.db.exists('Flege Patient',patient_id):
            #update patient#
            data = frappe.request.data or frappe.local.form_dict
            if data:
                #update patient_id
                
            pass
        else:
            frappe.local.response['http_status_code'] = 404
            frappe.local.response['message'] = 'patient not found'

@frappe.whitelist()
def delete_patient(**args):
    pass

@frappe.whitelist()
def get_patient(**args):
    pass
