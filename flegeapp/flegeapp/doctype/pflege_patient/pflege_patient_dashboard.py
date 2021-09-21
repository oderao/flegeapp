from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'pflege_order',
		'non_standard_fieldnames': {
			'Pflege Order': 'patient_id',
            'Pflege Subscription': 'party',
            'Pflege Delivery Note': 'patient_id'
		},
		'transactions': [
			{
				'label': _('Links'),
				'items': ['Pflege Order','Pflege Delivery Note', 'Pflege Subscription']
			},
		]
	}