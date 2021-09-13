from erpnext.accounts.doctype import subscription
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
        frappe.local.response['message'] = 'Patient update failed; no body params found'
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

def create_delivery_note(**args):
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
                    print('yes')
                    plan = frappe.get_doc('Subscription Plan',{'item':box.get('item')})
                    print(plan.billing_interval,'plan')
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
                'doctype': 'Subscription',
                'party_type':'Customer',
                'party':pflege_order.customer_name,
                'plans':subscription_plans,
                'start_date':pflege_order.order_date
            })
            subscription.save()
            return subscription
            
    except Exception as e:
        print(e)
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
            'subscription':args.subscription

        })
        delivery_note.insert(ignore_permissions=True)
        return delivery_note
        
    except:
        frappe.log_error(frappe.get_traceback(),'create delivery note failed')
        