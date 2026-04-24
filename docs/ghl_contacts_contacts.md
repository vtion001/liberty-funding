Skip to main content
￼￼
Highlevel API 2.0
Sign In



	•	Getting Started
	•	Authorization
	•	SDK Overview
	•	External Billing
	•	External Authentication
	•	User Context in Marketplace Apps
	•	MCP Server
	•	Marketplace Modules
	•	Marketplace Policies
	•	Changelog
	•	Country List
	•	FAQs
	•	
	•	OAuth 2.0
	•	Brand Boards
	•	Business
	•	Calendars
	•	Campaigns
	•	Companies
	•	Contacts
	◦	Introduction
	◦	Contacts
	▪	Get Contact
	▪	Update Contact
	▪	Delete Contact
	▪	Upsert Contact
	▪	Get Contacts By BusinessId
	▪	Create Contact
	▪	Get Contacts
	◦	Tasks
	◦	Appointments
	◦	Tags
	◦	Notes
	◦	Campaigns
	◦	Workflow
	◦	Bulk
	◦	Search
	◦	Followers
	•	Objects
	•	Associations
	•	Custom Fields V2
	•	Conversations
	•	Courses
	•	Email
	•	Forms
	•	Invoice
	•	Trigger Links
	•	Sub-Account (Formerly location)
	•	Media Storage
	•	Developer marketplace
	•	Blogs
	•	Funnels
	•	Opportunities
	•	Payments
	•	Products
	•	Saas
	•	Snapshots
	•	Social Planner
	•	Surveys
	•	Users
	•	Workflows
	•	LC Email
	•	Custom menus
	•	Voice AI
	•	Proposals
	•	Knowledge Base
	•	Conversation AI
	•	Phone System
	•	Store
	•	AI Agent Studio
	•	
	•	Webhook Integration Guide
	•	Webhook Logs Dashboard
	•	Webhook
	•	
	•	Contacts
	•	Contacts
Contacts
Documentation for Contacts API
📄️ Get Contact
Get Contact
📄️ Update Contact
Please find the list of acceptable values for the `country` field <a href='https://highlevel.stoplight.io/docs/integrations/ZG9jOjI4MzUzNDIy-country-list' target='_blank'>here</a>
📄️ Delete Contact
Delete Contact
📄️ Upsert Contact
Please find the list of acceptable values for the `country` field <a href='https://highlevel.stoplight.io/docs/integrations/ZG9jOjI4MzUzNDIy-country-list' target='_blank'>here</a><br/><br/>The Upsert API will adhere to the configuration defined under the “Allow Duplicate Contact” setting at the Location level. If the setting is configured to check both Email and Phone, the API will attempt to identify an existing contact based on the priority sequence specified in the setting, and will create or update the contact accordingly.<br/><br/>If two separate contacts already exist—one with the same email and another with the same phone—and an upsert request includes both the email and phone, the API will update the contact that matches the first field in the configured sequence, and ignore the second field to prevent duplication.
📄️ Get Contacts By BusinessId
Get Contacts By BusinessId
📄️ Create Contact
Please find the list of acceptable values for the `country` field <a href='https://highlevel.stoplight.io/docs/integrations/ZG9jOjI4MzUzNDIy-country-list' target='_blank'>here</a>
📄️ Get Contacts
Get Contacts

Previous
Introduction
Next
Get Contact
