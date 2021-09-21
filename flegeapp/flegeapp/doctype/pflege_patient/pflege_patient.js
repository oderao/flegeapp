// Copyright (c) 2021, Flege and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pflege Patient', {
	// refresh: function(frm) {

	// }
	care_box_type:function(frm){
		frm.clear_table('care_box')

		frappe.call({
			method:"flegeapp.utils.get_carebox_items",
			args:{
				"carebox":frm.doc.care_box_type
			},
			callback:function(r){
				if (r.message){
					var response = r.message
					console.log(r.message)
					for (let i = 0; i < response.length; i++) {
						var table = cur_frm.add_child('care_box')
						table.item = response[i].item
						table.quantity = response[i].quantity
						table.size = response[i].size
						cur_frm.refresh_field('care_box')
					}
					cur_frm.refresh_field('care_box')
					
				}
			}
		})

		//fill out carebox tables automatically
	}
});
