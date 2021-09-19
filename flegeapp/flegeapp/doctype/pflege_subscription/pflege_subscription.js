// Copyright (c) 2021, Flege and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pflege Subscription', {
	refresh: function(frm) {
        frm.set_query('party_type', function() {
			return {
				filters : {
					name: ['in', ['Pflege Patient']]
				}
			}
		});

	},

});
