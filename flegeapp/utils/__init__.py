from erpnext.accounts.doctype import subscription
import frappe
import json
from urllib.parse import urlparse
from urllib.parse import parse_qs
from erpnext.stock.utils import get_stock_balance


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
    ''' Create Patient from data sent from front end 
        patient ---> pflege_order ---> subscription ----> pflege delivery_note 
    '''
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
                                'pflege_order':pflege_order.name,
                                'date':frappe.utils.getdate()
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
                'city':args.city,
                'street_no':args.street_no,
                'country':args.country,
                'care_level':args.care_level,
                'care_box_type':args.care_box_type,
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
                #complete workflow
                #submit patient order
                #update pflege_order with patient_id
                if pflege_order:
                    pflege_order.patient_id = patient.name
                    pflege_order.submit()
                    args.pflege_order = pflege_order
                #create subscription
                subscription = create_subscription(pflege_order,carebox=args.care_box)
                if subscription:
                    args.subscription = subscription.name
                    #create delivery_note
                    delivery_note = create_delivery_note(args)  
                    
                    if delivery_note:
                        delivery_note.submit()
                        create_shipment(service='standard',delivery_note=delivery_note.as_dict())
                        #update subscription next_subscription date
                        subscription.submit()

                frappe.local.response['http_status_code'] = 200
                frappe.local.response['message'] = 'patient created successfully'
                frappe.local.response['data'] = {'patient_id':patient.name}
    except:
        frappe.log_error(frappe.get_traceback(),'create_patient')
        frappe.local.response['http_status_code'] = 400
        frappe.local.response['message'] = 'Invalid request,-invalid data sent'
        frappe.local.response['_server_messages'] = []
        frappe.local.response['exc'] = ''

def create_pflege_order(**args):
    ''' create sales order from patient order '''
    args = frappe._dict(args)
    try:
        customer_name = args.first_name + ' ' + args.last_name
        
        #check if customer is already existing:
        if frappe.db.exists('Customer',customer_name):
            customer = frappe.get_doc('Customer',customer_name)
        else:
            customer = frappe.new_doc('Customer')
            frappe.log_error(customer_name)
            customer.customer_name = customer_name
            customer.customer_group = 'Patient Group'
            customer.customer_type = 'Individual'
            customer.save()
        items = []
        for i in args.care_box:
            item = frappe.get_doc({
                'doctype':'Pflege Order Items',
                'item':i['item'],
                'rate':0,
                'quantity':i['quantity'],
                'amount':0
            })
            items.append(item)
        pflege_order = frappe.get_doc({
            'doctype':'Pflege Order',
            'customer_name':customer.name,
            'order_items':items,
            'order_date':frappe.utils.getdate()
        })
        pflege_order.insert(ignore_permissions=True)
        return pflege_order
    except:
        frappe.log_error(frappe.get_traceback(),'flege_order_creation_failed')

@frappe.whitelist()
def update_patient(**args):
    """ this handles the update of patient care box only"""
    url = frappe.request.url
    parsed_url = urlparse(url)
    query_dict = parse_qs(parsed_url.query)
    if not query_dict:
        frappe.local.response['http_status_code'] = 417
        frappe.local.response['message'] = 'Patient update failed; please add patient id to params'
    if query_dict and not query_dict.get('patient_id'):
        frappe.local.response['http_status_code'] = 400
        frappe.local.response['message'] = 'patient_id not in query'
    if query_dict and query_dict.get('patient_id'):
        #check if patient ID exists in the database
        patient_id = query_dict['patient_id'][0]
        if frappe.db.exists('Pflege Patient',patient_id):
            #update patient#
            data = frappe.request.data or frappe.local.form_dict
            if data:
                #update patient_id  
                frappe.local.response['http_status_code'] = 200
                frappe.local.response['message'] = 'patient-updated successfully'    
        else:

            frappe.local.response['http_status_code'] = 404
            frappe.local.response['message'] = 'patient not found'

@frappe.whitelist()
def delete_patient(**args):
    pass

@frappe.whitelist()
def get_patient(**args):
    pass


def create_subscription(pflege_order,carebox=[]):

    try:
        if carebox:
            #create subscription_plan for item if not existing
            #check if plan is existing
            subscription_plans = []
            for box in carebox:
                if frappe.db.exists('Subscription Plan',{'item':box.get('item')}):
                    #skip creation of subscription plan
                    plan = frappe.get_doc('Subscription Plan',{'item':box.get('item')})
                    subscription_plan_detail = frappe.get_doc({
                        'doctype':'Subscription Plan Detail',
                        'plan':plan.name,
                        'qty':box.get('quantity')
                    })
                    subscription_plans.append(subscription_plan_detail)
                    continue
            
                plan_name = 'Buy ' + box.get('item')
                #add validation for Subscription Plan to validate hook to check if item already exists
                plan = frappe.get_doc({
                    'doctype':'Subscription Plan',
                    'item':box['item'],
                    'plan_name':plan_name,
                    'price_determination':'Monthly Rate',
                    'billing_interval':'Month',
                    'billing_interval_count':1
                    
                })
                plan.save(ignore_permissions=True)

                subscription_plan_detail = frappe.get_doc({
                    'doctype':'Subscription Plan Detail',
                    'plan':plan.name,
                    'qty':box.get('quantity')
                })
               
                subscription_plans.append(subscription_plan_detail)
            #create actual subscription
           
            subscription = frappe.get_doc({
                'doctype': 'Pflege Subscription',
                'party_type':'Pflege Patient',
                'party':pflege_order.patient_id,
                'subscription_start_date':pflege_order.order_date,
                'subscription_end_date':frappe.utils.add_to_date(pflege_order.order_date,years=1),
            })
            subscription.save()
            return subscription
            
    except Exception as e:
        frappe.log_error(frappe.get_traceback(),'create_subscrption_failed')
        

def create_delivery_note(args):
    try:
        if not args.subscription:return

        delivery_note = frappe.get_doc({
            'doctype':'Pflege Delivery Note',
            'subscription':args.subscription,
            'pflege_order':args.pflege_order.name,
            'customer':args.pflege_order.customer_name,
            'items':args.pflege_order.order_items,
            'address':args.street_name,
            'zip_code':args.zip_code,
            'phone_number':args.phone_number,
            'delivery_note':args.note,
            'date':frappe.utils.getdate(),

        })
        delivery_note.insert(ignore_permissions=True)

        #update pflege subscription with delivery note

        table = frappe.get_doc({
            'doctype':'Pflege Delivery Note Table',
            'delivery_note':delivery_note.name,
            'date': delivery_note.date,
            'parent':args.subscription,
            'parentfield':'delivery',
            'parenttype':'Pflege Subscription'

        })
        table.save()
       
        frappe.db.commit()
        return delivery_note
        
    except:
        frappe.log_error(frappe.get_traceback(),'create delivery note failed')
        
@frappe.whitelist()
def create_shipment(service='',delivery_note=None):
    """ Create shipments using shipcloud apis """
    import base64,requests
    try:

        shipcloud = frappe.get_doc('Shipcloud Settings')
        if not shipcloud and shipcloud.create_shipment:return
        #service refers to the kind of shipment service example returns or one day shipping

        url = shipcloud.api_url
        #convert api to b64 encode
        api_key = shipcloud.get_password(fieldname='api_key').encode('ascii')
        api_key = base64.b64encode(api_key)
        api_key = api_key.decode('ascii')
        authorization_key = 'Basic ' + api_key
        headers = {'Authorization':authorization_key}
        
        #get patient from delivery note
        if not isinstance(delivery_note,dict):
            delivery_note = json.loads(delivery_note)
        patient_id = frappe.db.get_value('Pflege Order',delivery_note.get('pflege_order'),'patient_id')
        if patient_id:
            patient = frappe.get_doc('Pflege Patient',patient_id)

            data = {
                "to": {
                    "company": "",
                    "first_name": patient.first_name,
                    "last_name": patient.last_name,
                    "street": patient.street_name,
                    "street_no": patient.street_no or "0",
                    "city": patient.city, #use this as default city for now
                    "zip_code": patient.zip_code,
                    "country": patient.country
                },
                "package": {
                    "weight": shipcloud.weight,
                    "length": shipcloud.length,
                    "width": shipcloud.width,
                    "height": shipcloud.height,
                    "type": "parcel"
                },
                "carrier": shipcloud.carrier,
                "service": service,
                "reference_number": generate_random_reference(),
                "notification_email": patient.email_address,
                "create_shipping_label": True
                }
            #add return data if service==returns

            if service == 'returns':
                #returns should ideally come from the same place it was sent to
                data['from'] = data['to']

            r = requests.post(url,json=data,headers=headers)
            if r.status_code == 200:
                shipment_data = r.json()
                shipcloud_shipment = create_shipment_data(shipment_data=shipment_data)
                if shipcloud_shipment:
                    #update delivery note
                    frappe.db.set_value('Pflege Delivery Note',delivery_note.get('name'),'carrier',shipcloud.carrier)
                    
                    if service == 'standard':
                        frappe.db.set_value('Pflege Delivery Note',delivery_note.get('name'),'shipment_created',1)
                        frappe.db.set_value('Pflege Delivery Note',delivery_note.get('name'),'shipcloud_shipment',shipcloud_shipment.get('shipment_name'))
                        attach_to_delivery_note(delivery_note.get('name'),shipcloud_shipment.get('shipment_label_url'),service)
                        frappe.db.set_value('Pflege Delivery Note',delivery_note.get('name'),'shipcloud_shipment',shipcloud_shipment.get('shipment_name'))
                        frappe.db.set_value('Pflege Delivery Note',delivery_note.get('name'),'delivery_label',shipcloud_shipment.get('shipment_label_url'))

                    if service == 'returns':
                        frappe.db.set_value('Pflege Delivery Note',delivery_note.get('name'),'shipment_returned',1)
                        frappe.db.set_value('Pflege Delivery Note',delivery_note.get('name'),'shipcloud_return',shipcloud_shipment.get('shipment_name'))
                        attach_to_delivery_note(delivery_note.get('name'),shipcloud_shipment.get('shipment_label_url'),service)
                        frappe.db.set_value('Pflege Delivery Note',delivery_note.get('name'),'return_label',shipcloud_shipment.get('shipment_label_url'))

                    #attach shipment label to Delivery Note
                return {'message':True}
            else:
                frappe.log_error(r.content,'shipcloud_api_response')
                r.raise_for_status()
                return {'message':False}
    except:
        frappe.log_error(frappe.get_traceback(),'create_shipment_failed')

def generate_random_reference():
    import random,string
    ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k =10))
    return ref

def create_shipment_data(shipment_data={}):

    if not shipment_data:return
    shipment = frappe.new_doc('Shipcloud Shipment')
    shipment.shipment_id = shipment_data.get('id')
    shipment.carrier_tracking_no = shipment_data.get('carrier_tracking_no')
    shipment.tracking_url = shipment_data.get('tracking_url')
    shipment.label_url = shipment_data.get('label_url')
    shipment.price = shipment_data.get('price')
    shipment.save()
    frappe.db.commit()
    return {'shipment_name':shipment.name,'shipment_label_url':shipment.label_url}


def attach_to_delivery_note(delivery_note,label_url,service):
    fieldname = ''
    if service == 'standard':
        fieldname = 'shipping_label'
    if service == 'return_label':
        fieldname = 'return_label'

    ret = frappe.get_doc({
        "doctype": "File",
        "attached_to_doctype": 'Pflege Delivery Note',
        "attached_to_name": delivery_note,
        "attached_to_field":fieldname,
        "folder": 'Home',
        "file_name": '',
        "file_url": label_url,
        "is_private": 0,
        
    })
    ret.save(ignore_permissions=True)
    return ret

@frappe.whitelist()
def get_item(**args):
    """ This gets returns items as a dict"""
    url = frappe.request.url
    parsed_url = urlparse(url)
    query_dict = parse_qs(parsed_url.query)
    stock_balance = 0
    
    if not query_dict:
        frappe.local.response['http_status_code'] = 417
        frappe.local.response['message'] = 'Failed to get item; please add item params to url'
    
    if query_dict and not query_dict.get('item_name'):
        frappe.local.response['http_status_code'] = 400
        frappe.local.response['message'] = 'item_name not in query'
    
    if query_dict and query_dict.get('item_name'):
        #check if item exists in the database
        item_name = query_dict['item_name'][0]
        if frappe.db.exists('Item',item_name):
            item = frappe.get_all('Item',fields=["item_name","standard_rate","thumbnail","website_image"],filters={'disabled':0,'name':item_name})
            item = item[0]
            default_warehouse = frappe.db.get_value('Item Default',{'parent':item_name},'default_warehouse')
            if default_warehouse:
                stock_balance = get_stock_balance(item_name,default_warehouse)
            item['stock'] = stock_balance
            frappe.local.response['http_status_code'] = 200
            frappe.local.response['message'] = 'Item retrieved successfully' 
            frappe.local.response['data'] = item
        else:
            frappe.local.response['http_status_code'] = 404
            frappe.local.response['message'] = 'Item not found in Database'


    