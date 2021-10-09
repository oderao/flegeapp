// Copyright (c) 2021, Flege and contributors
// For license information, please see license.txt

frappe.ui.form.on('Pflege Patient', {
	refresh: function(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Create Subscription'),function () {
				if(frm.doc.has_subscription){
					frappe.msgprint('Subscription already existing for patient')
					return false
				}
			frappe.confirm('This will create a subscription for the Patient,Click yes to continue',function(){
				
				frappe.call({
					method:'flegeapp.utils.create_patient_subscription',
					args:{
						'patient':frm.doc,
					},
					freeze:true,
					callback:function(r) {
						console.log(r)
						
						if (r.message.status == false){
							frappe.msgprint('Create Subscription failed')
							return false
						}
						if (r.message.status == true){
							frappe.msgprint('Subscription Created Successfully')
						}
						cur_frm.refresh_field('has_subscription')
						cur_frm.refresh_fields()
						cur_frm.reload_doc()
					}
				})
				
				
				
				})
			})
			cur_frm.refresh_fields()	
			//cur_frm.reload_doc()
		}
		
	},
	care_box_type:function(frm){
		frm.clear_table('care_box')
		//fill out carebox tables automatically
		if(!frm.doc.care_box_type){

			return
		} 
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

		
	}
});
