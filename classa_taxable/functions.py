from __future__ import unicode_literals
import frappe
import erpnext
from frappe import auth
import datetime
import json, ast
from erpnext.accounts.utils import get_balance_on

@frappe.whitelist(allow_guest=True)
def sales_invoice_add(**kwargs):
    sales_invoice = frappe.get_doc(kwargs)
    sales_invoice.insert()
    sales_invoice.submit()
    sales_invoice_name = sales_invoice.name
    frappe.db.commit()
    if (sales_invoice_name):
        return sales_invoice_name
    else:
        return "Tax Invoice Not Migrated"
    
    #return kwargs


@frappe.whitelist(allow_guest=True)
def sales_invoice_cancel(si):
    sales_invoice = frappe.get_doc('Sales Invoice', {'remote_docname':si})
    sales_invoice.cancel()

