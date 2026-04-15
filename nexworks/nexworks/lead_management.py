import frappe
from frappe import _

def handle_lead_after_insert(doc, method):
	# Auto-assign Lead Owner if not assigned
	if not doc.lead_owner:
		doc.db_set('lead_owner', frappe.session.user)

	# Auto-create Task if involvement required Sales manager role
	if "Sales Manager" in frappe.get_roles(frappe.session.user):
		create_lead_task(doc)

def create_lead_task(doc):
	subject = f"Lead Evaluation – {doc.lead_name or doc.company}"
	if not frappe.db.exists("Task", {"subject": subject, "lead": doc.name}):
		task = frappe.get_doc({
			"doctype": "Task",
			"subject": subject,
			"status": "Open",
			"description": f"Evaluation for lead {doc.name}",
			"lead": doc.name
		})
		task.insert(ignore_permissions=True)
		# Assign task to current user
		from frappe.desk.form.assign_to import add
		add({
			"assign_to": [frappe.session.user],
			"doctype": "Task",
			"name": task.name,
			"description": subject
		})

def handle_opportunity_before_insert(doc, method):
	lead_name = doc.lead_from == "Lead" and doc.party_name
	if lead_name:
		lead = frappe.get_doc("Lead", lead_name)
		# Carry forward data
		doc.business_domain = lead.business_domain
		doc.description = lead.client_need_summary
		doc.detailed_client_requirement = lead.detailed_client_requirement

def handle_opportunity_on_update(doc, method):
	# Notify FC Team when moving to Under Review (FC)
	current_state = doc.workflow_state
	previous_state = frappe.db.get_value(doc.doctype, doc.name, "workflow_state")
	if current_state == "Under Review (FC)" and previous_state != "Under Review (FC)":
		notify_team(doc, "Functional Consultant", "Opportunity Under Review (FC)")

	# Notify Dev Team when moving to Under Review (Dev)
	if current_state == "Under Review (Dev)" and previous_state != "Under Review (Dev)":
		notify_team(doc, "Technical User", "Opportunity Under Review (Dev)")

def validate_opportunity_before_save(doc, method):
	# SOW uploaded -> Move to Proposal Stage validation
	if doc.workflow_state == "Proposal Submitted" and not doc.sow_document_link:
		frappe.throw(_("SOW Document Link is mandatory before moving to Proposal Submitted stage."))

def notify_team(doc, role, subject):
	users = frappe.get_all("Has Role", filters={"role": role}, fields=["parent"])
	recipients = [u.parent for u in users]
	if recipients:
		frappe.sendmail(
			recipients=recipients,
			subject=subject,
			message=f"Opportunity {doc.name} has moved to {doc.workflow_state}. Please review."
		)
