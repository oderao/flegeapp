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
	party:function(frm){
		frm.set_query('party',function() {
			return {
				query:'flegeapp.utils.get_patient_query',
			}
		})
	}

});
