from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'pflege_subscription',
		'non_standard_fieldnames': {
			'Pflege Delivery Note': 'subscription',
		},
		'transactions': [
			{
				'label': _('Links'),
				'items': ['Pflege Delivery Note', ]
			},
		]
	}