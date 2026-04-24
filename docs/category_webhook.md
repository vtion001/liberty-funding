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
	◦	AppInstall
	◦	AppointmentCreate
	◦	AppointmentDelete
	◦	AppointmentUpdate
	◦	AppUninstall
	◦	AssociationCreate
	◦	AssociationDelete
	◦	AssociationUpdate
	◦	CampaignStatusUpdate
	◦	ContactCreate
	◦	ContactDelete
	◦	ContactUpdate
	◦	ContactDndUpdate
	◦	ContactTagUpdate
	◦	ConversationUnreadWebhook
	◦	ExternalAuthConnected
	◦	InboundMessage
	◦	InvoiceCreate
	◦	InvoiceDelete
	◦	InvoicePaid
	◦	InvoicePartiallyPaid
	◦	InvoiceSent
	◦	InvoiceUpdate
	◦	InvoiceVoid
	◦	LCEmailStats
	◦	LocationCreate
	◦	LocationUpdate
	◦	NoteCreate
	◦	NoteDelete
	◦	NoteUpdate
	◦	ObjectSchemaCreate
	◦	ObjectSchemaUpdate
	◦	OpportunityAssignedToUpdate
	◦	OpportunityCreate
	◦	OpportunityDelete
	◦	OpportunityMonetaryValueUpdate
	◦	OpportunityStageUpdate
	◦	OpportunityStatusUpdate
	◦	OpportunityUpdate
	◦	OrderCreate
	◦	OrderStatusUpdate
	◦	OutboundMessage
	◦	PlanChange
	◦	PriceCreate
	◦	PriceDelete
	◦	PriceUpdate
	◦	ProductCreate
	◦	ProductDelete
	◦	ProductUpdate
	◦	ProviderOutboundMessage
	◦	RecordCreate
	◦	RecordDelete
	◦	RecordUpdate
	◦	RelationCreate
	◦	RelationDelete
	◦	SaaSPlanCreate
	◦	TaskComplete
	◦	TaskCreate
	◦	TaskDelete
	◦	UserCreate
	◦	VoiceAiCallEnd
	◦	UserDelete
	◦	UserUpdate
	•	
	•	Webhook
Webhook
This page defines all the webhook which are being sent whenever any specific activity happens.
📄️ AppInstall
Called whenever an app is installed
📄️ AppointmentCreate
Called whenever an appointment is created
📄️ AppointmentDelete
Called whenever an appointment is deleted
📄️ AppointmentUpdate
Called whenever an appointment is updated
📄️ AppUninstall
Called whenever an app is uninstalled
📄️ AssociationCreate
Overview
📄️ AssociationDelete
Overview
📄️ AssociationUpdate
Overview
📄️ CampaignStatusUpdate
Called whenever a campaign status is updated
📄️ ContactCreate
Called whenever a contact is created
📄️ ContactDelete
Called whenever a contact is deleted
📄️ ContactUpdate
Called whenever the specific fields in contact is updated
📄️ ContactDndUpdate
Called whenever a contact's dnd field is updated
📄️ ContactTagUpdate
Called whenever a contact's tag field is updated
📄️ ConversationUnreadWebhook
Called whenever a conversations unread status is updated
📄️ ExternalAuthConnected
Called whenever external authentication (OAuth2 or Basic) is connected successfully for an app/location/company.
📄️ InboundMessage
Called whenever a contact sends a message to the user.
📄️ InvoiceCreate
Called whenever an invoice is created
📄️ InvoiceDelete
Called whenever an invoice is deleted
📄️ InvoicePaid
Called whenever an invoice is paid
📄️ InvoicePartiallyPaid
Called whenever an invoice is partially paid
📄️ InvoiceSent
Called whenever an invoice is sent
📄️ InvoiceUpdate
Called whenever an invoice is updated
📄️ InvoiceVoid
Called whenever an invoice is marked as void
📄️ LCEmailStats
Called whenever an email is sent, gives the statistics of the said email.
📄️ LocationCreate
Called whenever a location is created.
📄️ LocationUpdate
Called whenever a location is updated.
📄️ NoteCreate
Called whenever a note is created
📄️ NoteDelete
Called whenever a note is deleted
📄️ NoteUpdate
Called whenever a note is updated
📄️ ObjectSchemaCreate
Overview
📄️ ObjectSchemaUpdate
Overview
📄️ OpportunityAssignedToUpdate
Called whenever an opportunity's AssignedTo field is updated
📄️ OpportunityCreate
Called whenever an opportunity is created
📄️ OpportunityDelete
Called whenever an opportunity is deleted
📄️ OpportunityMonetaryValueUpdate
Called whenever an opportunity's monetary value field is updated
📄️ OpportunityStageUpdate
Called whenever an opportunity's stage field is updated
📄️ OpportunityStatusUpdate
Called whenever an opportunity's status field is updated
📄️ OpportunityUpdate
Called whenever an opportunity is updated
📄️ OrderCreate
Called whenever an order is created
📄️ OrderStatusUpdate
Called whenever an order's status field updated
📄️ OutboundMessage
Called whenever a user sends a message to a contact.
📄️ PlanChange
Called whenever user changes the plan for a paid app.
📄️ PriceCreate
Called whenever a price is created
📄️ PriceDelete
Called whenever a price is deleted
📄️ PriceUpdate
Called whenever a price is updated
📄️ ProductCreate
Called whenever a product is created
📄️ ProductDelete
Called whenever a product is deleted
📄️ ProductUpdate
Called whenever a product is updated
📄️ ProviderOutboundMessage
Called whenever a user sends a message to a contact and has a custom provider as the default channel in the settings.
📄️ RecordCreate
Overview
📄️ RecordDelete
Overview
📄️ RecordUpdate
Overview
📄️ RelationCreate
Overview
📄️ RelationDelete
Overview
📄️ SaaSPlanCreate
Overview
📄️ TaskComplete
Called whenever a task is completed
📄️ TaskCreate
Called whenever a task is created
📄️ TaskDelete
Called whenever a task is deleted
📄️ UserCreate
Called whenever a user is created
📄️ VoiceAiCallEnd
Called whenever a Voice AI call ends for a sub-account.
📄️ UserDelete
Called whenever a user is deleted
📄️ UserUpdate
Called whenever a user is updated
Previous
Webhook Logs Dashboard
Next
AppInstall
