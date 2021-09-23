// Copyright (c) 2021, Flege and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pflege Order', {
	// refresh: function(frm) {

	// }
	setup: function(frm) {
		frm.custom_make_buttons = {
			'Delivery Note': 'Delivery Note',
			
		}
		
	},
	patient_id: function (frm){
		
		frm.set_query('patient_id', function(frm){
			return {
				query:'flegeapp.utils.get_patient_query',
			}

		})
	}
});
