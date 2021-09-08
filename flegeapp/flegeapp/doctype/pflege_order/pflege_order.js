// Copyright (c) 2021, Flege and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pflege Order', {
	// refresh: function(frm) {

	// }
	setup: function(frm) {
		console.log('steup')
		frm.custom_make_buttons = {
			'Delivery Note': 'Delivery Note',
			
		}
		
	},
});
