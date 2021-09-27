from erpnext.accounts.doctype import subscription
import frappe
from flegeapp.utils import create_shipment
from operator import attrgetter

def daily():
    run_daily_tasks()

def run_daily_tasks():
    try:
        #get all flege subscription where next_subscription_date = current_date

        subscriptions = frappe.get_all('Pflege Subscription',filters={'next_subscription_date':frappe.utils.getdate(),
                                    'status':'Active','docstatus':1},fields=['name','party'])
        for subscription in subscriptions:
            #this will get the latest delivery note linked to a subscription
            if frappe.db.exists('Pflege Delivery Note',{'subscription':subscription.name}):
                print('yes')
                delivery_note = frappe.get_last_doc('Pflege Delivery Note',{'subscription':subscription.name})
                new_delivery_note = frappe.copy_doc(delivery_note)
                new_delivery_note.shipcloud_shipment = ''
                new_delivery_note.delivery_label = ''
                new_delivery_note.return_label = ''
                new_delivery_note.shipment_created = ''
                
                new_delivery_note.date = frappe.utils.getdate()
                new_delivery_note.submit()

                #update subscription with latest delivery_note created
                table = frappe.get_doc({
                    'doctype':'Pflege Delivery Note Table',
                    'delivery_note':new_delivery_note.name,
                    'date': new_delivery_note.date,
                    'parent':subscription.name,
                    'parentfield':'delivery',
                    'parenttype':'Pflege Subscription'

                })
                
                subscription_doc = frappe.get_doc('Pflege Subscription',subscription.name)
                table.idx = len(subscription_doc.delivery) + 1
                table.save()
                subscription_doc.delivery.append(table)
                subscription_doc.add_date() #update next date
                subscription_doc.save()
                create_shipments(dict(new_delivery_note.as_dict()),subscription.party)
                frappe.db.commit()
    except Exception as e:
        frappe.log_error(frappe.get_traceback(),'create_delivery_note_and_shipment_failed')
        
def create_shipments(delivery_note,patient_id):
    #create shipments for submitted delivery notes
    create_shipment(delivery_note=delivery_note)



def sort_list(delivery_list):
    modified = delivery_list.modified
    if isinstance(delivery_list.modified,str):
        modified = frappe.utils.get_datetime(delivery_list.modified)
    return modified