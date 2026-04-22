import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def install():
	create_roles()
	create_custom_fields(get_custom_fields())
	create_property_setters()
	create_workflows()

def after_migrate():
	install()

def create_roles():
	roles = ["Functional Consultant", "Technical User", "Sales Manager"]
	for role in roles:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({
				"doctype": "Role",
				"role_name": role,
				"desk_access": 1
			}).insert(ignore_permissions=True)

def get_custom_fields():
	return {
		"Lead": [
			{
				"fieldname": "business_domain",
				"label": "Business Domain",
				"fieldtype": "Select",
				"options": "\nIT\nManufacturing\nRetail\nServices\nHealthcare\nEducation",
				"insert_after": "company",
				"reqd": 1
			},
			{
				"fieldname": "client_need_summary",
				"label": "Client Need Summary",
				"fieldtype": "Small Text",
				"insert_after": "business_domain",
				"reqd": 1
			},
			{
				"fieldname": "meeting_schedule",
				"label": "Meeting Schedule",
				"fieldtype": "Datetime",
				"insert_after": "client_need_summary",
				"reqd": 1
			},
			{
				"fieldname": "detailed_client_requirement",
				"label": "Detailed Client Requirement",
				"fieldtype": "Text Editor",
				"insert_after": "meeting_schedule"
			},
			{
				"fieldname": "priority",
				"label": "Priority",
				"fieldtype": "Select",
				"options": "\nLow\nMedium\nHigh",
				"insert_after": "detailed_client_requirement"
			},
			{
				"fieldname": "expected_budget",
				"label": "Expected Budget",
				"fieldtype": "Currency",
				"insert_after": "priority"
			},
			{
				"fieldname": "location",
				"label": "Location",
				"fieldtype": "Data",
				"insert_after": "expected_budget"
			}
		],
		"Opportunity": [
			{
				"fieldname": "business_domain",
				"label": "Business Domain",
				"fieldtype": "Select",
				"options": "\nIT\nManufacturing\nRetail\nServices\nHealthcare\nEducation",
				"insert_after": "company"
			},
			{
				"fieldname": "detailed_client_requirement",
				"label": "Detailed Client Requirement",
				"fieldtype": "Text Editor",
				"insert_after": "description"
			},
			{
				"fieldname": "project_type",
				"label": "Project Type",
				"fieldtype": "Select",
				"options": "\nImplementation\nCustomization\nSupport",
				"insert_after": "detailed_client_requirement"
			},
			{
				"fieldname": "modules_required",
				"label": "Modules Required",
				"fieldtype": "MultiSelect",
				"options": "CRM\nSelling\nBuying\nStock\nAccounting\nHR\nProjects\nSupport",
				"insert_after": "project_type"
			},
			{
				"fieldname": "fc_comments",
				"label": "FC Comments",
				"fieldtype": "Small Text",
				"insert_after": "modules_required"
			},
			{
				"fieldname": "matching_project_references",
				"label": "Matching Project References",
				"fieldtype": "Small Text",
				"insert_after": "fc_comments"
			},
			{
				"fieldname": "suggested_modules",
				"label": "Suggested Modules",
				"fieldtype": "Small Text",
				"insert_after": "matching_project_references"
			},
			{
				"fieldname": "complexity_level",
				"label": "Complexity Level",
				"fieldtype": "Select",
				"options": "\nLow\nMedium\nHigh",
				"insert_after": "suggested_modules"
			},
			{
				"fieldname": "existing_codebase_availability",
				"label": "Existing Codebase Availability",
				"fieldtype": "Select",
				"options": "\nYes\nNo",
				"insert_after": "complexity_level"
			},
			{
				"fieldname": "customization_scope",
				"label": "Customization Scope",
				"fieldtype": "Small Text",
				"insert_after": "existing_codebase_availability"
			},
			{
				"fieldname": "integration_requirements",
				"label": "Integration Requirements",
				"fieldtype": "Small Text",
				"insert_after": "customization_scope"
			},
			{
				"fieldname": "technical_comments",
				"label": "Technical Comments",
				"fieldtype": "Small Text",
				"insert_after": "integration_requirements"
			},
			{
				"fieldname": "sow_document_link",
				"label": "SOW Document Link",
				"fieldtype": "Data",
				"insert_after": "technical_comments"
			}
		],
		"Task": [
			{
				"fieldname": "lead",
				"label": "Lead",
				"fieldtype": "Link",
				"options": "Lead",
				"insert_after": "subject"
			}
		]
	}

def create_property_setters():
	lead_mandatory = ["lead_name", "mobile_no", "email_id", "company", "source"]
	for field in lead_mandatory:
		if not frappe.db.exists("Property Setter", {"doc_type": "Lead", "field_name": field, "property": "reqd"}):
			frappe.make_property_setter({
				"doctype": "Lead",
				"fieldname": field,
				"property": "reqd",
				"value": 1,
				"property_type": "Check"
			})

def create_workflows():
	# Create Lead Workflow
	if not frappe.db.exists("Workflow", "Lead Workflow"):
		workflow = frappe.get_doc({
			"doctype": "Workflow",
			"workflow_name": "Lead Workflow",
			"document_type": "Lead",
			"workflow_state_field": "workflow_state",
			"is_active": 1,
			"states": [
				{"state": "New Lead", "allow_edit": "All"},
				{"state": "Contacted", "allow_edit": "All"},
				{"state": "Meeting Scheduled", "allow_edit": "All"},
				{"state": "Converted", "allow_edit": "All"}
			],
			"transitions": [
				{"state": "New Lead", "action": "Contact", "next_state": "Contacted", "allowed": "Sales User"},
				{"state": "Contacted", "action": "Schedule Meeting", "next_state": "Meeting Scheduled", "allowed": "Sales User"},
				{"state": "Meeting Scheduled", "action": "Convert", "next_state": "Converted", "allowed": "Sales User"}
			]
		})
		workflow.insert(ignore_permissions=True)

	# Create Opportunity Workflow
	if not frappe.db.exists("Workflow", "Opportunity Workflow"):
		workflow = frappe.get_doc({
			"doctype": "Workflow",
			"workflow_name": "Opportunity Workflow",
			"document_type": "Opportunity",
			"workflow_state_field": "workflow_state",
			"is_active": 1,
			"states": [
				{"state": "Requirement Gathering", "allow_edit": "All"},
				{"state": "Under Review (FC)", "allow_edit": "All"},
				{"state": "Under Review (Dev)", "allow_edit": "All"},
				{"state": "SOW Prepared", "allow_edit": "All"},
				{"state": "Proposal Submitted", "allow_edit": "All"},
				{"state": "Won", "allow_edit": "All"},
				{"state": "Lost", "allow_edit": "All"}
			],
			"transitions": [
				{"state": "Requirement Gathering", "action": "Submit for FC Review", "next_state": "Under Review (FC)", "allowed": "Sales User"},
				{"state": "Under Review (FC)", "action": "Submit for Dev Review", "next_state": "Under Review (Dev)", "allowed": "Functional Consultant"},
				{"state": "Under Review (Dev)", "action": "Prepare SOW", "next_state": "SOW Prepared", "allowed": "Technical User"},
				{"state": "SOW Prepared", "action": "Submit Proposal", "next_state": "Proposal Submitted", "allowed": "Sales User"},
				{"state": "Proposal Submitted", "action": "Mark Won", "next_state": "Won", "allowed": "Sales User"},
				{"state": "Proposal Submitted", "action": "Mark Lost", "next_state": "Lost", "allowed": "Sales User"}
			]
		})
		workflow.insert(ignore_permissions=True)
