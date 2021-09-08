# Copyright (c) 2021, Flege and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from functools import reduce

class PflegeDeliveryNote(Document):
	def validate(self):
		self.set_total_number_of_items()

	def on_submit(self):
		#set status to submitted.
		self.status = 'Submitted'

	def set_total_number_of_items(self):
		if self.items:
			total = reduce(lambda x,y:x+y, [i.quantity for i in self.items])
			self.total_number_of_items = total
