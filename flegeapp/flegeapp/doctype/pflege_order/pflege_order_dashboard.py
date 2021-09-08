from __future__ import unicode_literals
from frappe import _

def get_data():
	return {
		'fieldname': 'pflege_order',
		'non_standard_fieldnames': {
			'Pflege Delivery Note': 'pflege_order',
		},
		'transactions': [
			{
				'label': _('Fulfillment'),
				'items': ['Pflege Delivery Note', ]
			},
		]
	}