import frappe


def daily():
    run_daily_tasks()

def run_daily_tasks():
    #get all flege subscription where next_subscription_date = current_date

    subscriptions = frappe.get_all('Pflege Subscription',filters={'next_subscription_date':frappe.utils.getdate(),
                                'status':'Active','docstatus':1})


