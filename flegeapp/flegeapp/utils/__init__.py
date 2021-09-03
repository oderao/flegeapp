import frappe


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


def create_patient(**args):
    if args:
        patient_id = 'FLG-PAT-.####'
        
        patient = frappe.get_doc({'doctype':'Flege Patient',
                                  'title':args.title,
                                  'first_name':args.first_name,
                                  'last_name':args.last_name,
                                  'street_name':args.street_name,
                                  'date_of_birth':args.date_of_birth,
                                  'zip_code':args.zip_code,
                                  'country':args.country,
                                  'care_level':args.care_level,
                                  'care_box':care_box,
                                  'phone_number':args.phone_number,
                                  'email_address':args.email_address
        })
