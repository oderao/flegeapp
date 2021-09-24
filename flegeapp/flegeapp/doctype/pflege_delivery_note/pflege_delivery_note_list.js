frappe.listview_settings['Pflege Delivery Note'] = {
	add_fields: ["status" ],
	get_indicator: function (doc) {
		if (doc.status === "Shipped" ) {
			// Active
			return [__("Shipped"), "green", "status,=,Active"];
		} else if (doc.status === "Shipment Returned" ) {
			// on hold
			return [__("Shipment Returned"), "grey", "status,=,Shipment Returned"];
		} else if (doc.status === "Submitted") {
			return [__("Submitted"), "blue", "status,=,Submitted"];
		} else if (doc.status === "Shipment Created") {
			return [__("Shipment Created"), "orange", "status,=,Shipment Create"];
		}
	},
}