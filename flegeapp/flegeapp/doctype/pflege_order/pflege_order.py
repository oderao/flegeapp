# Copyright (c) 2021, Flege and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document

class PflegeOrder(Document):
	
	def validate(self):
		pass

	def on_submit(self):
		#set status to submitted.
		self.status = 'Submitted'