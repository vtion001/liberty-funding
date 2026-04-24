Skip to main content
￼￼
Highlevel API 2.0
Sign In



	•	Getting Started
	•	Authorization
	◦	Private Integrations Token
	◦	OAuth 2.0
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
	•	
	•	Authorization
On this page
Authorization
Authorization is the process of granting or denying access to resources based on a user's verified identity and permissions. It determines what a user can do within a system after they have been authenticated (proven their identity). Essentially, it's about verifying that a user has the right to access specific resources or perform certain actions.

HighLevel currently supports two types of authorization:
	•	Private Integration Token
	•	OAuth 2.0 Flow

When should I use a Private Integration Token?
You should use a Private Integration Token if:
	•	Your use case involves accessing our API endpoints for internal purposes.
	•	If you don't need webhooks or custom design or pages.
	•	If you need to access only 1 sub-account at a time.
Example use cases:
	•	Internal data synchronization
	•	Custom reporting dashboards
	•	Automated tasks within your own system

When should I use OAuth 2.0 Flow?
You should use OAuth 2.0 Flow if:
	•	You're developing a full-scale integration intended for public use.
	•	Your integration requires features like webhooks and custom modules.
	•	You need advanced security features and standardized authorization management.
Example use cases:
	•	Third-party applications
	•	Creating custom conversation providers/custom workflow actions and triggers, etc.
	•	Services requiring secure user authorization



Previous
How to Update Your APP
Next
Private Integrations Token
	•	HighLevel currently supports two types of authorization:
	◦	When should I use a Private Integration Token?
	◦	When should I use OAuth 2.0 Flow?
