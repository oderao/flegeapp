from __future__ import unicode_literals
import frappe
import wrapt
__version__ = '0.0.1'

from flegeapp.overrides import generate_invoice
from erpnext.accounts.doctype.subscription import subscription

subscription.Subscription.generate_invoice = generate_invoice