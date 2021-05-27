import frappe
import datetime


@frappe.whitelist()
def create_babs_forms(babsyear: int, babsmonth: int, babslimit: int):
    company = frappe.defaults.get_user_default("Company")

    start_date = datetime.date(year=int(babsyear), month=int(babsmonth), day=1)
    end_date = frappe.utils.get_last_day(start_date)

    babsmap = {}

    customers = frappe.get_all("Customer", filters={"customer_type": "Company", "tax_id": ["not in", None]},
                               fields=["tax_id", "name"])
    for customer in customers:
        sales_invoice_count_since_start = frappe.db.count("Sales Invoice",
                                                          filters={"docstatus": 1, "company": company,
                                                                   "customer": customer.name,
                                                                   "posting_date": [">=", start_date],
                                                                   "is_return": 0})
        sales_invoice_count_since_end = frappe.db.count("Sales Invoice",
                                                        filters={"docstatus": 1, "company": company,
                                                                 "customer": customer.name,
                                                                 "posting_date": [">", end_date],
                                                                 "is_return": 0})
        sales_invoice_count = sales_invoice_count_since_start - sales_invoice_count_since_end

        if sales_invoice_count > 0:
            customer_total_since_start = frappe.db.get_all("Sales Invoice",
                                                           filters={"docstatus": 1, "company": company,
                                                                    "customer": customer.name,
                                                                    "posting_date": [">=", start_date],
                                                                    "is_return": 0},
                                                           fields=["sum(base_net_total) as sales_total", "customer"],
                                                           group_by="customer")
            customer_total_since_end = frappe.db.get_all("Sales Invoice",
                                                         filters={"docstatus": 1, "company": company,
                                                                  "customer": customer.name,
                                                                  "posting_date": [">", end_date],
                                                                  "is_return": 0},
                                                         fields=["sum(base_net_total) as sales_total", "customer"],
                                                         group_by="customer")
            if len(customer_total_since_end) > 0:
                customer_total = int(
                    customer_total_since_start[0].sales_total - customer_total_since_end[0].sales_total)
            else:
                customer_total = int(customer_total_since_start[0].sales_total)

            if babsmap.get(customer.tax_id) is None:
                babsmap[customer.tax_id] = dict(customer=customer.name,
                                                bs_invoice_count=sales_invoice_count,
                                                bs_total=customer_total)

        sales_invoice_count_since_start = frappe.db.count("Sales Invoice",
                                                          filters={"docstatus": 1, "company": company,
                                                                   "customer": customer.name,
                                                                   "posting_date": [">=", start_date],
                                                                   "is_return": 1})
        sales_invoice_count_since_end = frappe.db.count("Sales Invoice",
                                                        filters={"docstatus": 1, "company": company,
                                                                 "customer": customer.name,
                                                                 "posting_date": [">", end_date],
                                                                 "is_return": 1})
        sales_invoice_count = sales_invoice_count_since_start - sales_invoice_count_since_end

        if sales_invoice_count > 0:
            customer_total_since_start = frappe.db.get_all("Sales Invoice",
                                                           filters={"docstatus": 1, "company": company,
                                                                    "customer": customer.name,
                                                                    "posting_date": [">=", start_date],
                                                                    "is_return": 1},
                                                           fields=["sum(base_net_total) as sales_total", "customer"],
                                                           group_by="customer")
            customer_total_since_end = frappe.db.get_all("Sales Invoice",
                                                         filters={"docstatus": 1, "company": company,
                                                                  "customer": customer.name,
                                                                  "posting_date": [">", end_date],
                                                                  "is_return": 1},
                                                         fields=["sum(base_net_total) as sales_total", "customer"],
                                                         group_by="customer")
            if len(customer_total_since_end) > 0:
                customer_total = int(
                    customer_total_since_start[0].sales_total - customer_total_since_end[0].sales_total)
            else:
                customer_total = int(customer_total_since_start[0].sales_total)

            if babsmap.get(customer.tax_id) is None:
                babsmap[customer.tax_id] = dict(supplier=customer.name,
                                                ba_invoice_count=sales_invoice_count,
                                                ba_total=customer_total)
            else:
                babsmap[customer.tax_id]["supplier"] = customer.name
                babsmap[customer.tax_id]["ba_invoice_count"] = sales_invoice_count
                babsmap[customer.tax_id]["ba_total"] = customer_total

    suppliers = frappe.get_all("Supplier", filters={"supplier_type": "Company", "tax_id": ["not in", None]},
                               fields=["tax_id", "name"])

    for supplier in suppliers:
        purchase_invoice_count_since_start = frappe.db.count("Purchase Invoice",
                                                             filters={"docstatus": 1, "company": company,
                                                                      "supplier": supplier.name,
                                                                      "posting_date": [">=", start_date],
                                                                      "is_return": 0})
        purchase_invoice_count_since_end = frappe.db.count("Purchase Invoice",
                                                           filters={"docstatus": 1, "company": company,
                                                                    "supplier": supplier.name,
                                                                    "posting_date": [">", end_date],
                                                                    "is_return": 0})
        purchase_invoice_count = purchase_invoice_count_since_start - purchase_invoice_count_since_end
        if purchase_invoice_count > 0:
            supplier_total_since_start = frappe.db.get_all("Purchase Invoice",
                                                           filters={"docstatus": 1, "company": company,
                                                                    "supplier": supplier.name,
                                                                    "posting_date": [">=", start_date],
                                                                    "is_return": 0},
                                                           fields=["sum(base_net_total) as purchase_total", "supplier"],
                                                           group_by="supplier")
            supplier_total_since_end = frappe.db.get_all("Purchase Invoice",
                                                         filters={"docstatus": 1, "company": company,
                                                                  "supplier": supplier.name,
                                                                  "posting_date": [">", end_date],
                                                                  "is_return": 0},
                                                         fields=["sum(base_net_total) as purchase_total", "supplier"],
                                                         group_by="supplier")
            if len(supplier_total_since_end) > 0:
                supplier_total = int(supplier_total_since_start[0].purchase_total - supplier_total_since_end[
                    0].purchase_total)
            else:
                supplier_total = int(supplier_total_since_start[0].purchase_total)

            if babsmap.get(supplier.tax_id) is None:
                babsmap[supplier.tax_id] = dict(supplier=supplier.name,
                                                ba_invoice_count=purchase_invoice_count,
                                                ba_total=supplier_total)
            else:
                babsmap[supplier.tax_id]["supplier"] = supplier.name
                babsmap[supplier.tax_id]["ba_invoice_count"] += purchase_invoice_count
                babsmap[supplier.tax_id]["ba_total"] += supplier_total

        purchase_invoice_count_since_start = frappe.db.count("Purchase Invoice",
                                                             filters={"docstatus": 1, "company": company,
                                                                      "supplier": supplier.name,
                                                                      "posting_date": [">=", start_date],
                                                                      "is_return": 1})
        purchase_invoice_count_since_end = frappe.db.count("Purchase Invoice",
                                                           filters={"docstatus": 1, "company": company,
                                                                    "supplier": supplier.name,
                                                                    "posting_date": [">", end_date],
                                                                    "is_return": 1})
        purchase_invoice_count = purchase_invoice_count_since_start - purchase_invoice_count_since_end
        if purchase_invoice_count > 0:
            supplier_total_since_start = frappe.db.get_all("Purchase Invoice",
                                                           filters={"docstatus": 1, "company": company,
                                                                    "supplier": supplier.name,
                                                                    "posting_date": [">=", start_date],
                                                                    "is_return": 1},
                                                           fields=["sum(base_net_total) as purchase_total", "supplier"],
                                                           group_by="supplier")
            supplier_total_since_end = frappe.db.get_all("Purchase Invoice",
                                                         filters={"docstatus": 1, "company": company,
                                                                  "supplier": supplier.name,
                                                                  "posting_date": [">", end_date],
                                                                  "is_return": 1},
                                                         fields=["sum(base_net_total) as purchase_total", "supplier"],
                                                         group_by="supplier")
            if len(supplier_total_since_end) > 0:
                supplier_total = int(supplier_total_since_start[0].purchase_total - supplier_total_since_end[
                    0].purchase_total)
            else:
                supplier_total = int(supplier_total_since_start[0].purchase_total)

            if babsmap.get(supplier.tax_id) is None:
                babsmap[supplier.tax_id] = dict(customer=supplier.name,
                                                bs_invoice_count=purchase_invoice_count,
                                                bs_total=supplier_total)
            else:
                babsmap[supplier.tax_id]["customer"] = supplier.name
                babsmap[supplier.tax_id]["bs_invoice_count"] += purchase_invoice_count
                babsmap[supplier.tax_id]["bs_total"] += supplier_total

    for tax_id in babsmap.keys():
        if babsmap.get(tax_id).get("ba_total") >= int(babslimit):
            if not frappe.db.exists({
                "doctype": "BA BS Form",
                "company": company,
                "year": babsyear,
                "month": babsmonth,
                "tax_id": tax_id
            }):
                new_doc = frappe.new_doc("BA BS Form")
                new_doc.company = company
                new_doc.year = babsyear
                new_doc.month = babsmonth
                new_doc.tax_id = tax_id
                if babsmap.get(tax_id).get("supplier") is not None:
                    new_doc.supplier = babsmap.get(tax_id).get("supplier")
                new_doc.ba_invoice_count = babsmap.get(tax_id).get("ba_invoice_count")
                new_doc.ba_total = babsmap.get(tax_id).get("ba_total")
                new_doc.insert()
            else:
                frappe_doc = frappe.get_doc({
                    "doctype": "BA BS Form",
                    "company": company,
                    "year": babsyear,
                    "month": babsmonth,
                    "tax_id": tax_id
                })
                if frappe_doc.form_sent == 0:
                    if babsmap.get(tax_id).get("supplier") is not None:
                        frappe_doc.supplier = babsmap.get(tax_id).get("supplier")
                    frappe_doc.ba_invoice_count = babsmap.get(tax_id).get("ba_invoice_count")
                    frappe_doc.ba_total = babsmap.get(tax_id).get("ba_total")
                    frappe_doc.save()

        if babsmap.get(tax_id).get("bs_total") >= int(babslimit):
            if not frappe.db.exists({
                "doctype": "BA BS Form",
                "company": company,
                "year": babsyear,
                "month": babsmonth,
                "tax_id": tax_id
            }):
                new_doc = frappe.new_doc("BA BS Form")
                new_doc.company = company
                new_doc.year = babsyear
                new_doc.month = babsmonth
                new_doc.tax_id = tax_id
                if babsmap.get(tax_id).get("customer") is not None:
                    new_doc.customer = babsmap.get(tax_id).get("customer")
                new_doc.bs_invoice_count = babsmap.get(tax_id).get("bs_invoice_count")
                new_doc.bs_total = babsmap.get(tax_id).get("bs_total")
                new_doc.insert()
            else:
                frappe_doc = frappe.get_doc({
                    "doctype": "BA BS Form",
                    "company": company,
                    "year": babsyear,
                    "month": babsmonth,
                    "tax_id": tax_id
                })
                if frappe_doc.form_sent == 0:
                    if babsmap.get(tax_id).get("customer") is not None:
                        frappe_doc.customer = babsmap.get(tax_id).get("customer")
                    frappe_doc.bs_invoice_count = babsmap.get(tax_id).get("bs_invoice_count")
                    frappe_doc.bs_total = babsmap.get(tax_id).get("bs_total")
                    frappe_doc.save()

    return frappe.utils.now_datetime()


def get_dynamic_links_of_type(document, doctype, return_type):
    if has_dynamic_links_of_type(document, doctype, return_type):
        names = []
        for name in frappe.get_all("Dynamic Link",
                                   filters={"link_name": document, "link_doctype": doctype, "parenttype": return_type},
                                   fields=["parent"]):
            names.append(name.parent)
        return names
    else:
        return None


def get_dynamic_link_count_of_type(document, doctype, return_type):
    if frappe.db.count("Dynamic Link",
                       filters={"link_name": document, "link_doctype": doctype, "parenttype": return_type
                                }) is not None:
        return frappe.db.count("Dynamic Link",
                               filters={"link_name": document, "link_doctype": doctype, "parenttype": return_type})
    else:
        return 0


def has_dynamic_links_of_type(document, doctype, return_type):
    if frappe.db.count("Dynamic Link",
                       filters={"link_name": document, "link_doctype": doctype, "parenttype": return_type
                                }) is not None:
        if frappe.db.count("Dynamic Link",
                           filters={"link_name": document, "link_doctype": doctype, "parenttype": return_type}) > 0:
            return True
        else:
            return False
    else:
        return False


@frappe.whitelist()
def send_babs_form(form_name):
    babs_doc = frappe.get_doc("BA BS Form", form_name)
    recipients = []
    if babs_doc.customer is not None:
        if frappe.get_value("Customer", babs_doc.customer, "email_id") is not None:
            recipients.append(frappe.get_value("Customer", babs_doc.customer, "email_id"))
        elif babs_doc.supplier is None:
            frappe.msgprint(msg="Please define an e-mail address for {0}.".format(babs_doc.customer),
                            title="Customer")
    elif babs_doc.supplier is not None:
        if has_dynamic_links_of_type(babs_doc.supplier, "Supplier", "Contact"):
            for name in get_dynamic_links_of_type(babs_doc.supplier, "Supplier", "Contact"):
                if frappe.db.get_value("Contact", name, "email_id") is not None:
                    recipients.append(frappe.db.get_value("Contact", name, "email_id"))
        elif has_dynamic_links_of_type(babs_doc.supplier, "Supplier", "Address"):
            for name in get_dynamic_links_of_type(babs_doc.supplier, "Supplier", "Address"):
                if frappe.db.get_value("Address", name, "email_id") is not None:
                    recipients.append(frappe.db.get_value("Address", name, "email_id"))
        else:
            frappe.msgprint(msg="Please define an e-mail address for {0}.".format(babs_doc.supplier),
                            title="Supplier")
    message = ""
    email_args = {
        "recipients": recipients,
        "message": message,
        "subject": "[{0}] BA BS BİLDİRİMİ MUTABAKAT FORMU".format(frappe.defaults.get_user_default("Company")),
        "attachments": [frappe.attach_print(doctype="BA BS Form", name=form_name, file_name="{name}.pdf".format(
            name=form_name.replace(" ", "-").replace("/", "-")), print_format="BA BS Bildirimi Mutabakat Formu",
                                            lang="tr",
                                            print_letterhead=False)],
        "reference_doctype": "BA BS Form",
        "reference_name": form_name
    }
    frappe.utils.background_jobs.enqueue(method=frappe.sendmail, queue='short', timeout=300, is_async=True,
                                         **email_args)
