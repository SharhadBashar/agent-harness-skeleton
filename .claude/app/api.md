# InspectlyAI Backend API Reference

All `v0` endpoints are mounted under the version prefix (typically `/v0`). Authentication uses an API key (see `app/core/security.py`).

## Root / Health

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/` | Welcome message. | none | `{ message: str }` |
| GET | `/status` | API liveness check. | none | `{ message: str }` |
| GET | `/db_status` | Database connectivity check. | none | `{ message: str, error?: str }` |
| GET | `/v0/` | v0 welcome message. | none | `{ message: str }` |
| GET | `/v0/status` | v0 liveness check. | none | `{ message: str }` |

---

## Shared Schemas (referenced below)

**Enums (`app/schema/types.py`):**
- `User_Type`: `admin` | `client` | `realtor` | `vendor`
- `Vendor_Type`: `general` | `structural` | `electrician` | `plumber` | `painter` | `cleaner` | `hvac` | `roofing` | `insulation` | `drywall` | `plaster` | `carpentry` | `landscaping` | `other`
- `Login`: `email` | `phone` | `gmail`
- `Status` (issue): `open` | `review` | `in_progress` | `completed`
- `Bid_Status`: `received` | `accepted` | `rejected`
- `Assessment_Status`: `received` | `accepted` | `rejected`
- `Review_Status`: `pending` | `approved` | `rejected`
- `Dispute_Status`: `open` | `in_review` | `resolved` | `closed`
- `Task_Status`: `pending` | `in_progress` | `completed` | `failed`
- `Task_Type`: `extract_issues` | `extract_images`

**Body Schemas (Pydantic models — output is the resource row, typically same fields plus an integer `id` and timestamps):**

- `Attachments`: `{ issue_id: int, user_id: int, name: str, type: str, url: str }`
- `Comments`: `{ issue_id: int, user_id: int, comment: str }`
- `Notes`: `{ report_id: int, user_id: int, note: str }`
- `Listings`: `{ user_id: int, address: str, city: str, state: str, country: str, postal_code: str, image_url?: str }`
- `Reports`: `{ user_id: int, listing_id: int, aws_link?: str, name: str, review_status?: str }`
- `Reports_Simple`: `{ user_id: int, listing_id: int, name: str }`
- `Report_Offers`: `{ report_id: int, vendor_id?: int, price: float, status: Bid_Status, user_last_viewed?: str, comment_vendor?: str, comment_client?: str }`
- `Report_Assessments`: `{ report_id: int, user_id: int, user_type: User_Type, interaction_id: str, users_interaction_id: str, start_time: str, end_time: str, status: Assessment_Status, user_last_viewed?: str, min_assessment_time?: int }`
- `Report_Assessments_Delete`: `{ report_id: int, interaction_id: str }`
- `Report_Assessment_Comments`: `{ report_assessment_id: int, user_id: int, comment: str }`
- `Issues`: `{ report_id?: int, listing_id: int, type: str, vendor_id?: int, description?: str, summary?: str, severity?: str, status: Status, active: bool, image_urls?: str[], review_status?: str }`
- `Issue_Images`: `{ issue_id: int, url: str }`
- `Issue_Offers`: `{ issue_id: int, vendor_id?: int, price: float, status: Bid_Status, user_last_viewed?: str, comment_vendor?: str, comment_client?: str }`
- `Issue_Assessments`: `{ issue_id: int, user_id: int, user_type: User_Type, interaction_id: str, users_interaction_id: str, start_time: str, end_time: str, status: Assessment_Status, user_last_viewed?: str, min_assessment_time?: int }`
- `Issue_Assessments_Delete`: `{ issue_id: int, interaction_id: str }`
- `Issue_Assessment_Comments`: `{ issue_assessment_id: int, user_id: int, comment: str }`
- `Issue_Disputes`: `{ issue_offer_id: int, status: Dispute_Status, status_message?: str }`
- `Issue_Dispute_Messages`: `{ message: str, user_type: User_Type }`
- `Issue_Dispute_Attachments`: `{ attachment_url: str, user_type: User_Type }`
- `Users`: `{ user_type: User_Types, firebase_id: str }`
- `Clients`: `{ user_id: int, first_name: str, last_name: str, email: str, phone?: str, address?: str, city?: str, state?: str, country?: str, postal_code?: str }`
- `Realtors`: `{ realtor_user_id: int, realtor_firm_id: int, first_name: str, last_name: str, email: str, phone: str, address: str, city: str, state: str, country: str, postal_code: str, rating?: int=-1, review?: str }`
- `Vendors`: `{ vendor_user_id: int, vendor_type: Vendor_Types, vendor_types: str, code: str, license?: str, verified: bool=false, name: str, email: str, phone: str, address: str, city: str, state: str, country: str, postal_code: str, rating?: int=-1, review?: str, years_of_experience?: int, service_area?: str, response_time?: str, insurance?: str, warranty?: str }`
- `Vendor_Employees`: `{ vendor_id: int, first_name: str, last_name: str, skills: str, email?: str, phone?: str, address?: str, city: str, state?: str, country?: str, postal_code?: str, rating?: int=-1, review?: str, years_of_experience?: int }`
- `User_Logins`: `{ user_id: int, email_login: bool=false, email?: str, phone_login: bool=false, phone?: str, gmail_login: bool=false, gmail?: str }`
- `User_Sessions`: `{ user_id: int, login: Login, login_time: str, logout_time?: str, authentication_code: str }`
- `Realtor_Firms`: `{ name: str, code: str, email: str, phone: str, address: str, city: str, state: str, country: str, postal_code: str, rating?: int=-1, review?: str }`
- `Client_Reviews`: `{ user_id: int, client_user_id: int, status: Review_Status=pending, rating: float, review: str }`
- `Realtor_Reviews`: `{ user_id: int, realtor_user_id: int, status: Review_Status=pending, rating: float, review: str }`
- `Vendor_Reviews`: `{ user_id: int, vendor_user_id: int, status: Review_Status=pending, rating: float, review: str }`
- `Payments`: `{ user_id: int, amount: float, expiry_date: str, stripe_payment_id: str, stripe_user_id: str }`
- `User_Stripe_Information`: `{ user_id: int, stripe_user_id: str }`
- `Tasks`: `{ report_id: int, task_type: Task_Type, status: Task_Status }`

> For all routes below: unless otherwise noted, list/read endpoints return the resource row(s) (i.e. schema fields plus DB-generated `id`/timestamp columns); create/update endpoints return the created/updated row.

---

## `/v0/attachments` — Attachments (file attachments on issues)

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/attachments/` | List all attachments. | none | `Attachments[]` |
| GET | `/v0/attachments/{id}` | Get one attachment by id. | path: `id: int` | `Attachments` |
| GET | `/v0/attachments/issue/{issue_id}` | List attachments for an issue. | path: `issue_id: int` | `Attachments[]` |
| GET | `/v0/attachments/user/{user_id}` | List attachments uploaded by a user. | path: `user_id: int` | `Attachments[]` |
| POST | `/v0/attachments/` | Create an attachment. | body: `Attachments` | `Attachments` |
| PUT | `/v0/attachments/{id}` | Update an attachment. | path: `id`; body: `Attachments` | `Attachments` |
| DELETE | `/v0/attachments/{id}` | Delete an attachment. | path: `id: int` | `{ deleted: true }` (CRUD-dependent) |

## `/v0/client_reviews` — Reviews about clients (left by realtors/vendors)

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/client_reviews/` | List all client reviews. | none | `Client_Reviews[]` |
| GET | `/v0/client_reviews/{id}` | Get one client review. | path: `id: int` | `Client_Reviews` |
| GET | `/v0/client_reviews/user_id/{user_id}` | Reviews authored by a user (reviewer). | path: `user_id: int` | `Client_Reviews[]` |
| GET | `/v0/client_reviews/client_user_id/{client_user_id}` | Reviews about a given client user. | path: `client_user_id: int` | `Client_Reviews[]` |
| POST | `/v0/client_reviews/` | Create a client review. | body: `Client_Reviews` | `Client_Reviews` |
| PUT | `/v0/client_reviews/{id}` | Update a client review. | path: `id`; body: `Client_Reviews` | `Client_Reviews` |
| DELETE | `/v0/client_reviews/{id}` | Delete a client review. | path: `id: int` | `{ deleted: true }` |

## `/v0/clients` — Client profiles

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/clients/` | List all clients. | none | `Clients[]` |
| GET | `/v0/clients/{id}` | Get one client by client id. | path: `id: int` | `Clients` |
| GET | `/v0/clients/user_id/{user_id}` | Get client by underlying `user_id`. | path: `user_id: int` | `Clients` |
| POST | `/v0/clients/` | Create a client profile. | body: `Clients` | `Clients` |
| PUT | `/v0/clients/{id}` | Update a client profile. | path: `id`; body: `Clients` | `Clients` |
| DELETE | `/v0/clients/{id}` | Delete a client profile. | path: `id: int` | `{ deleted: true }` |

## `/v0/comments` — Comments on issues

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/comments/` | List all comments. | none | `Comments[]` |
| GET | `/v0/comments/{id}` | Get one comment. | path: `id: int` | `Comments` |
| GET | `/v0/comments/issue/{issue_id}` | Comments for a given issue. | path: `issue_id: int` | `Comments[]` |
| GET | `/v0/comments/user/{user_id}` | Comments authored by a user. | path: `user_id: int` | `Comments[]` |
| POST | `/v0/comments/` | Create a comment. | body: `Comments` | `Comments` |
| PUT | `/v0/comments/{id}` | Update a comment. | path: `id`; body: `Comments` | `Comments` |
| DELETE | `/v0/comments/{id}` | Delete a comment. | path: `id: int` | `{ deleted: true }` |

## `/v0/images` — Image upload

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| POST | `/v0/images/` | Upload an image file (e.g. to AWS S3) and get back its hosted URL. | `multipart/form-data` with `image: File` | `{ url: str, ... }` (CRUD-dependent — typically `{ url }` or upload result) |

## `/v0/issue_assessment_comments` — Comments on issue assessments

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/issue_assessment_comments/` | List all issue-assessment comments. | none | `Issue_Assessment_Comments[]` |
| GET | `/v0/issue_assessment_comments/{id}` | Get one issue-assessment comment. | path: `id: int` | `Issue_Assessment_Comments` |
| GET | `/v0/issue_assessment_comments/issue_assessment/{issue_assessment_id}` | Comments for a given issue assessment. | path: `issue_assessment_id: int` | `Issue_Assessment_Comments[]` |
| GET | `/v0/issue_assessment_comments/user/{user_id}` | Comments authored by a user. | path: `user_id: int` | `Issue_Assessment_Comments[]` |
| GET | `/v0/issue_assessment_comments/user/{user_id}/issue_assessment/{issue_assessment_id}` | Comments from a user on a specific issue assessment. | path: `user_id: int`, `issue_assessment_id: int` | `Issue_Assessment_Comments[]` |
| POST | `/v0/issue_assessment_comments/` | Create an issue-assessment comment. | body: `Issue_Assessment_Comments` | `Issue_Assessment_Comments` |
| PUT | `/v0/issue_assessment_comments/{id}` | Update an issue-assessment comment. | path: `id`; body: `Issue_Assessment_Comments` | `Issue_Assessment_Comments` |
| DELETE | `/v0/issue_assessment_comments/{id}/issue_assessment/{issue_assessment_id}` | Delete a comment scoped to its issue assessment. | path: `id: int`, `issue_assessment_id: int` | `{ deleted: true }` |

## `/v0/issue_assessments` — Issue assessment sessions

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/issue_assessments/` | List all issue assessments. | none | `Issue_Assessments[]` |
| GET | `/v0/issue_assessments/{id}` | Get one issue assessment by id. | path: `id: int` | `Issue_Assessments` |
| GET | `/v0/issue_assessments/issue/{issue_id}` | Assessments for an issue. | path: `issue_id: int` | `Issue_Assessments[]` |
| GET | `/v0/issue_assessments/users_interaction/{users_interaction_id}` | Assessments for a given users-interaction string. | path: `users_interaction_id: str` | `Issue_Assessments[]` |
| GET | `/v0/issue_assessments/user_id/{user_id}` | Assessments authored by a user. | path: `user_id: int` | `Issue_Assessments[]` |
| GET | `/v0/issue_assessments/client_id_users_interaction_id/{client_id}` | Assessments by client id grouped by users-interaction id. | path: `client_id: int` | `Issue_Assessments[]` |
| GET | `/v0/issue_assessments/vendor_id_users_interaction_id/{vendor_id}` | Assessments by vendor id grouped by users-interaction id. | path: `vendor_id: int` | `Issue_Assessments[]` |
| POST | `/v0/issue_assessments/` | Create an issue assessment. | body: `Issue_Assessments` | `Issue_Assessments` |
| PUT | `/v0/issue_assessments/{id}` | Update an issue assessment. | path: `id`; body: `Issue_Assessments` | `Issue_Assessments` |
| DELETE | `/v0/issue_assessments/{id}` | Delete an assessment (uses body params). | path: `id: int`; body: `Issue_Assessments_Delete` | `{ deleted: true }` |

## `/v0/issue_dispute_attachments` — File attachments on issue disputes

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/issue_dispute_attachments/{issue_dispute_id}` | Attachments for a given issue dispute. | path: `issue_dispute_id: int` | `Issue_Dispute_Attachments[]` |
| POST | `/v0/issue_dispute_attachments/` | Add an attachment to an issue dispute. | query: `issue_dispute_id: int`; body: `Issue_Dispute_Attachments` | `Issue_Dispute_Attachments` |
| DELETE | `/v0/issue_dispute_attachments/{id}` | Delete an issue-dispute attachment. | path: `id: int` | `{ deleted: true }` |

## `/v0/issue_dispute_messages` — Messages within an issue dispute thread

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/issue_dispute_messages/{issue_dispute_id}` | Messages for a given issue dispute. | path: `issue_dispute_id: int` | `Issue_Dispute_Messages[]` |
| POST | `/v0/issue_dispute_messages/` | Post a message to an issue dispute. | query: `issue_dispute_id: int`; body: `Issue_Dispute_Messages` | `Issue_Dispute_Messages` |

## `/v0/issue_disputes` — Disputes raised on issue offers

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/issue_disputes/` | List all issue disputes. | none | `Issue_Disputes[]` |
| GET | `/v0/issue_disputes/{id}` | Get a single issue dispute. | path: `id: int` | `Issue_Disputes` |
| GET | `/v0/issue_disputes/issue_offer/{issue_offer_id}` | Disputes for a given issue offer. | path: `issue_offer_id: int` | `Issue_Disputes[]` |
| GET | `/v0/issue_disputes/issue_offer/{issue_offer_id}/open` | Open disputes for a given issue offer. | path: `issue_offer_id: int` | `Issue_Disputes[]` |
| GET | `/v0/issue_disputes/issue_offer/{issue_offer_id}/details` | Full dispute view: status + chronologically merged messages and attachments. | path: `issue_offer_id: int` | `{ status: Dispute_Status, status_message?: str, items: { type: 'message'\|'attachment', user_type: User_Type, message?: str, attachment_url?: str, created_at: str }[] }` |
| POST | `/v0/issue_disputes/` | Open a new issue dispute. | body: `Issue_Disputes` | `Issue_Disputes` |
| PUT | `/v0/issue_disputes/{id}` | Update an issue dispute. | path: `id`; body: `Issue_Disputes` | `Issue_Disputes` |

## `/v0/issue_offers` — Vendor bids/offers on issues

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/issue_offers/` | List all issue offers. | none | `Issue_Offers[]` |
| GET | `/v0/issue_offers/{id}` | Get one issue offer. | path: `id: int` | `Issue_Offers` |
| GET | `/v0/issue_offers/issue/{issue_id}` | Offers for an issue. | path: `issue_id: int` | `Issue_Offers[]` |
| GET | `/v0/issue_offers/vendor/{vendor_id}` | Offers submitted by a vendor. | path: `vendor_id: int` | `Issue_Offers[]` |
| GET | `/v0/issue_offers/vendor/{vendor_id}/issue/{issue_id}` | Offers from a specific vendor on a specific issue. | path: `vendor_id: int`, `issue_id: int` | `Issue_Offers[]` |
| POST | `/v0/issue_offers/` | Submit an issue offer. | body: `Issue_Offers` | `Issue_Offers` |
| PUT | `/v0/issue_offers/{id}` | Update an issue offer. | path: `id`; body: `Issue_Offers` | `Issue_Offers` |
| DELETE | `/v0/issue_offers/{id}` | Delete an issue offer (requires issue_id in body). | path: `id: int`; body: `{ issue_id: int }` | `{ deleted: true }` |

## `/v0/issues` — Inspection issues (paginated)

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/issues/` | List all issues, paginated. | query: `page: int`, `size: int` (fastapi-pagination) | `Page<Issues>` = `{ items: Issues[], total: int, page: int, size: int, pages: int }` |
| GET | `/v0/issues/total` | Count of all issues. | query: `vendor_assigned?: bool=false` | `int` |
| GET | `/v0/issues/total/filter` | Count of issues matching filters. | query: `type?: str`, `city?: str`, `state?: str`, `search?: str`, `vendor_assigned?: bool=false` | `int` |
| GET | `/v0/issues/filter` | Paginated issues filtered by type/city/state/search. | query: filters above + pagination | `Page<Issues>` |
| GET | `/v0/issues/{id}` | Get one issue. | path: `id: int` | `Issues` |
| GET | `/v0/issues/report/{report_id}` | Issues belonging to a report. | path: `report_id: int` | `Issues[]` |
| GET | `/v0/issues/listing/{listing_id}` | Issues for a listing. | path: `listing_id: int` | `Issues[]` |
| GET | `/v0/issues/vendor/{vendor_id}` | Issues assigned to a vendor. | path: `vendor_id: int` | `Issues[]` |
| GET | `/v0/issues/addresses/all` | All listing addresses associated with issues. | none | `{ address fields }[]` |
| POST | `/v0/issues/addresses/issue_ids` | Listing addresses for the given issue ids. | body: `{ issue_ids: int[] }` | `{ address fields }[]` |
| GET | `/v0/issues/address/{id}` | Listing address for one issue. | path: `id: int` | `{ address fields }` |
| POST | `/v0/issues/` | Create an issue (async). | body: `Issues` | `Issues` |
| PUT | `/v0/issues/{id}` | Update an issue. | path: `id`; body: `Issues` | `Issues` |
| DELETE | `/v0/issues/{id}` | Delete an issue. | path: `id: int` | `{ deleted: true }` |

## `/v0/listings` — Property listings (paginated)

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/listings/` | List all listings, paginated. | query: `page`, `size` | `Page<Listings>` |
| GET | `/v0/listings/{id}` | Get one listing. | path: `id: int` | `Listings` |
| GET | `/v0/listings/user/{user_id}` | Listings owned by a user. | path: `user_id: int` | `Listings[]` |
| POST | `/v0/listings/` | Create a listing. | body: `Listings` | `Listings` |
| PUT | `/v0/listings/{id}` | Update a listing. | path: `id`; body: `Listings` | `Listings` |
| DELETE | `/v0/listings/{id}` | Delete a listing. | path: `id: int` | `{ deleted: true }` |

## `/v0/notes` — Free-form notes on reports

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/notes/` | List all notes. | none | `Notes[]` |
| GET | `/v0/notes/{id}` | Get one note. | path: `id: int` | `Notes` |
| GET | `/v0/notes/report/{report_id}` | Notes for a report. | path: `report_id: int` | `Notes[]` |
| GET | `/v0/notes/user/{user_id}` | Notes authored by a user. | path: `user_id: int` | `Notes[]` |
| POST | `/v0/notes/` | Create a note. | body: `Notes` | `Notes` |
| PUT | `/v0/notes/{id}` | Update a note. | path: `id`; body: `Notes` | `Notes` |
| DELETE | `/v0/notes/{id}` | Delete a note. | path: `id: int` | `{ deleted: true }` |

## `/v0/payments` — Payment records

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/payments/` | List all payments. | none | `Payments[]` |
| GET | `/v0/payments/{id}` | Get one payment. | path: `id: int` | `Payments` |
| GET | `/v0/payments/user/{user_id}` | Payments for a user. | path: `user_id: int` | `Payments[]` |
| POST | `/v0/payments/` | Create a payment record. | body: `Payments` | `Payments` |
| DELETE | `/v0/payments/{id}` | Delete a payment. | path: `id: int` | `{ deleted: true }` |

## `/v0/realtor_firms` — Realtor brokerage/firms

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/realtor_firms/` | List all realtor firms. | none | `Realtor_Firms[]` |
| GET | `/v0/realtor_firms/{id}` | Get one realtor firm. | path: `id: int` | `Realtor_Firms` |
| POST | `/v0/realtor_firms/` | Create a realtor firm. | body: `Realtor_Firms` | `Realtor_Firms` |
| PUT | `/v0/realtor_firms/{id}` | Update a realtor firm. | path: `id`; body: `Realtor_Firms` | `Realtor_Firms` |
| DELETE | `/v0/realtor_firms/{id}` | Delete a realtor firm. | path: `id: int` | `{ deleted: true }` |

## `/v0/realtor_reviews` — Reviews of realtors

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/realtor_reviews/` | List all realtor reviews. | none | `Realtor_Reviews[]` |
| GET | `/v0/realtor_reviews/{id}` | Get one realtor review. | path: `id: int` | `Realtor_Reviews` |
| GET | `/v0/realtor_reviews/user_id/{user_id}` | Reviews authored by a user (reviewer). | path: `user_id: int` | `Realtor_Reviews[]` |
| GET | `/v0/realtor_reviews/realtor_user_id/{realtor_user_id}` | Reviews about a given realtor user. | path: `realtor_user_id: int` | `Realtor_Reviews[]` |
| POST | `/v0/realtor_reviews/` | Create a realtor review. | body: `Realtor_Reviews` | `Realtor_Reviews` |
| PUT | `/v0/realtor_reviews/{id}` | Update a realtor review. | path: `id`; body: `Realtor_Reviews` | `Realtor_Reviews` |
| DELETE | `/v0/realtor_reviews/{id}` | Delete a realtor review. | path: `id: int` | `{ deleted: true }` |

## `/v0/realtors` — Realtor profiles

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/realtors/` | List all realtors. | none | `Realtors[]` |
| GET | `/v0/realtors/{id}` | Get one realtor by id. | path: `id: int` | `Realtors` |
| GET | `/v0/realtors/realtor_user_id/{user_id}` | Get realtor by underlying `user_id`. | path: `user_id: int` | `Realtors` |
| POST | `/v0/realtors/` | Create a realtor profile. | body: `Realtors` | `Realtors` |
| PUT | `/v0/realtors/{id}` | Update a realtor profile. | path: `id`; body: `Realtors` | `Realtors` |
| DELETE | `/v0/realtors/{id}` | Delete a realtor profile. | path: `id: int` | `{ deleted: true }` |

## `/v0/report_assessment_comments` — Comments on report assessments

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/report_assessment_comments/` | List all report-assessment comments. | none | `Report_Assessment_Comments[]` |
| GET | `/v0/report_assessment_comments/{id}` | Get one report-assessment comment. | path: `id: int` | `Report_Assessment_Comments` |
| GET | `/v0/report_assessment_comments/report_assessment/{report_assessment_id}` | Comments for a given report assessment. | path: `report_assessment_id: int` | `Report_Assessment_Comments[]` |
| GET | `/v0/report_assessment_comments/user/{user_id}` | Comments authored by a user. | path: `user_id: int` | `Report_Assessment_Comments[]` |
| GET | `/v0/report_assessment_comments/user/{user_id}/report_assessment/{report_assessment_id}` | Comments from a user on a specific report assessment. | path: `user_id: int`, `report_assessment_id: int` | `Report_Assessment_Comments[]` |
| POST | `/v0/report_assessment_comments/` | Create a report-assessment comment. | body: `Report_Assessment_Comments` | `Report_Assessment_Comments` |
| PUT | `/v0/report_assessment_comments/{id}` | Update a report-assessment comment. | path: `id`; body: `Report_Assessment_Comments` | `Report_Assessment_Comments` |
| DELETE | `/v0/report_assessment_comments/{id}/report_assessment/{report_assessment_id}` | Delete a comment scoped to its report assessment. | path: `id: int`, `report_assessment_id: int` | `{ deleted: true }` |

## `/v0/report_assessments` — Report assessment sessions

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/report_assessments/` | List all report assessments. | none | `Report_Assessments[]` |
| GET | `/v0/report_assessments/{id}` | Get one report assessment. | path: `id: int` | `Report_Assessments` |
| GET | `/v0/report_assessments/report/{report_id}` | Assessments for a report. | path: `report_id: int` | `Report_Assessments[]` |
| GET | `/v0/report_assessments/users_interaction/{users_interaction_id}` | Assessments for a users-interaction string. | path: `users_interaction_id: str` | `Report_Assessments[]` |
| GET | `/v0/report_assessments/user_id/{user_id}` | Assessments authored by a user. | path: `user_id: int` | `Report_Assessments[]` |
| GET | `/v0/report_assessments/client_id_users_interaction_id/{client_id}` | Assessments by client id grouped by users-interaction id. | path: `client_id: int` | `Report_Assessments[]` |
| GET | `/v0/report_assessments/vendor_id_users_interaction_id/{vendor_id}` | Assessments by vendor id grouped by users-interaction id. | path: `vendor_id: int` | `Report_Assessments[]` |
| POST | `/v0/report_assessments/` | Create a report assessment. | body: `Report_Assessments` | `Report_Assessments` |
| PUT | `/v0/report_assessments/{id}` | Update a report assessment. | path: `id`; body: `Report_Assessments` | `Report_Assessments` |
| DELETE | `/v0/report_assessments/{id}` | Delete a report assessment (uses body params). | path: `id: int`; body: `Report_Assessments_Delete` | `{ deleted: true }` |

## `/v0/report_offers` — Vendor bids/offers on reports

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/report_offers/` | List all report offers. | none | `Report_Offers[]` |
| GET | `/v0/report_offers/{id}` | Get one report offer. | path: `id: int` | `Report_Offers` |
| GET | `/v0/report_offers/report/{report_id}` | Offers on a report. | path: `report_id: int` | `Report_Offers[]` |
| GET | `/v0/report_offers/vendor/{vendor_id}` | Offers submitted by a vendor. | path: `vendor_id: int` | `Report_Offers[]` |
| GET | `/v0/report_offers/vendor/{vendor_id}/report/{report_id}` | Offers from a specific vendor on a specific report. | path: `vendor_id: int`, `report_id: int` | `Report_Offers[]` |
| POST | `/v0/report_offers/` | Submit a report offer. | body: `Report_Offers` | `Report_Offers` |
| PUT | `/v0/report_offers/{id}` | Update a report offer. | path: `id`; body: `Report_Offers` | `Report_Offers` |
| DELETE | `/v0/report_offers/{id}` | Delete a report offer (requires report_id in body). | path: `id: int`; body: `{ report_id: int }` | `{ deleted: true }` |

## `/v0/reports` — Inspection reports (paginated, with PDF extract)

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/reports/` | List all reports, paginated. | query: `page`, `size` | `Page<Reports>` |
| GET | `/v0/reports/{id}` | Get one report. | path: `id: int` | `Reports` |
| GET | `/v0/reports/user/{user_id}` | Reports owned by a user. | path: `user_id: int` | `Reports[]` |
| GET | `/v0/reports/listing/{listing_id}` | Reports for a listing. | path: `listing_id: int` | `Reports[]` |
| POST | `/v0/reports/` | Create a report (async). | body: `Reports` | `Reports` |
| POST | `/v0/reports/extract/issues` | Upload a PDF property report and kick off a background task that extracts issues from it. | `multipart/form-data`: `user_id: int`, `listing_id: int`, `name: str`, `property_report: File` (PDF only) | `{ report_id: int, task_id: int, aws_link: str }` |
| PUT | `/v0/reports/{id}` | Update a report. | path: `id`; body: `Reports` | `Reports` |
| DELETE | `/v0/reports/{id}` | Delete a report. | path: `id: int` | `{ deleted: true }` |

## `/v0/stripe` — Stripe checkout & webhook

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| POST | `/v0/stripe/checkout/create-session` | Create a Stripe Checkout session for a client/vendor/offer triple. | body: `Checkout_Session_Request { client_id: int, vendor_id: int, offer_id: int }` | `{ session_url: str, session: object }` |
| POST | `/v0/stripe/checkout/webhook` | Stripe webhook receiver — handles `checkout.session.*` events. | raw request body + header `Stripe-Signature: str` | `{ status: str }` (200) or `{ status: 'error', detail: str }` (4xx/5xx) |

## `/v0/stripe_payments` — Stripe payments (stubbed)

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| _(no active routes)_ | | The router exists but all handlers are commented out — no endpoints currently exposed. | — | — |

## `/v0/stripe_user_information` — Mapping between app users and Stripe customers

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/stripe_user_information/` | List all user→stripe records. | none | `User_Stripe_Information[]` |
| GET | `/v0/stripe_user_information/{id}` | Get one record. | path: `id: int` | `User_Stripe_Information` |
| GET | `/v0/stripe_user_information/user/{user_id}` | Stripe info for a given app user. | path: `user_id: int` | `User_Stripe_Information` |
| GET | `/v0/stripe_user_information/stripe_user_id/{stripe_user_id}` | Lookup by Stripe customer id. | path: `stripe_user_id: str` | `User_Stripe_Information` |
| POST | `/v0/stripe_user_information/` | Create a user→stripe mapping. | body: `User_Stripe_Information` | `User_Stripe_Information` |
| POST | `/v0/stripe_user_information/existing-user/{user_id}` | Create a Stripe customer for an existing app user (server-side Stripe call). | path: `user_id: int` | `User_Stripe_Information` |
| PUT | `/v0/stripe_user_information/{id}` | Update a user→stripe mapping. | path: `id`; body: `User_Stripe_Information` | `User_Stripe_Information` |
| DELETE | `/v0/stripe_user_information/{id}` | Delete a user→stripe mapping. | path: `id: int` | `{ deleted: true }` |

## `/v0/tasks` — Background tasks (e.g. issue/image extraction)

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/tasks/` | List all tasks. | none | `Tasks[]` |
| GET | `/v0/tasks/{id}` | Get one task. | path: `id: int` | `Tasks` |
| GET | `/v0/tasks/report/{report_id}` | Tasks tied to a report. | path: `report_id: int` | `Tasks[]` |
| POST | `/v0/tasks/` | Create a task. | body: `Tasks` | `Tasks` |
| PUT | `/v0/tasks/{id}` | Update a task (e.g. status transitions). | path: `id`; body: `Tasks` | `Tasks` |

## `/v0/user_logins` — User login channels (email/phone/gmail)

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/user_logins/` | List all user-login records. | none | `User_Logins[]` |
| GET | `/v0/user_logins/{id}` | Get one user-login record. | path: `id: int` | `User_Logins` |
| GET | `/v0/user_logins/user/{user_id}` | Login record for a user. | path: `user_id: str` | `User_Logins` |
| POST | `/v0/user_logins/` | Create a login record. | body: `User_Logins` | `User_Logins` |
| PUT | `/v0/user_logins/{id}` | Update a login record. | path: `id`; body: `User_Logins` | `User_Logins` |
| DELETE | `/v0/user_logins/{id}` | Delete a login record. | path: `id: int` | `{ deleted: true }` |

## `/v0/user_sessions` — User session tracking

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/user_sessions/` | List all user sessions. | none | `User_Sessions[]` |
| GET | `/v0/user_sessions/{id}` | Get one session. | path: `id: int` | `User_Sessions` |
| GET | `/v0/user_sessions/user/{user_id}` | Latest/active session for a user. | path: `user_id: str` | `User_Sessions` |
| POST | `/v0/user_sessions/` | Create a session (login). | body: `User_Sessions` | `User_Sessions` |
| PUT | `/v0/user_sessions/{id}` | Update logout time for a session. | path: `id: int`; query: `logout_time: str` | `User_Sessions` |

## `/v0/user_types` — User type lookup (admin/client/realtor/vendor)

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/user_types/` | List all user types. | none | `User_Types[]` |
| GET | `/v0/user_types/{id}` | Get one user type. | path: `id: int` | `User_Types` |
| POST | `/v0/user_types/` | Create a user type. | body: `User_Types` | `User_Types` |
| PUT | `/v0/user_types/{id}` | Update a user type. | path: `id`; body: `User_Types` | `User_Types` |
| DELETE | `/v0/user_types/{id}` | Delete a user type. | path: `id: int` | `{ deleted: true }` |

## `/v0/users` — Base user records (linked to Firebase)

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/users/` | List all users. | none | `Users[]` |
| GET | `/v0/users/{id}` | Get one user. | path: `id: int` | `Users` |
| GET | `/v0/users/firebase/{firebase_id}` | Look up a user by their Firebase id. | path: `firebase_id: str` | `Users` |
| POST | `/v0/users/` | Create a user (async). | body: `Users` | `Users` |
| PUT | `/v0/users/{id}` | Update a user. | path: `id`; body: `Users` | `Users` |
| DELETE | `/v0/users/{id}` | Delete a user. | path: `id: int` | `{ deleted: true }` |

## `/v0/vendor_employees` — Employees attached to a vendor company

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/vendor_employees/vendor_id/{vendor_id}` | Employees of a given vendor. | path: `vendor_id: int` | `Vendor_Employees[]` |
| GET | `/v0/vendor_employees/{id}` | Get one vendor employee. | path: `id: int` | `Vendor_Employees` |
| POST | `/v0/vendor_employees/` | Create a vendor employee. | body: `Vendor_Employees` | `Vendor_Employees` |
| PUT | `/v0/vendor_employees/{id}` | Update a vendor employee. | path: `id`; body: `Vendor_Employees` | `Vendor_Employees` |
| DELETE | `/v0/vendor_employees/{id}/{vendor_id}` | Delete a vendor employee (scoped to vendor). | path: `id: int`, `vendor_id: int` | `{ deleted: true }` |

## `/v0/vendor_reviews` — Reviews of vendors

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/vendor_reviews/` | List all vendor reviews. | none | `Vendor_Reviews[]` |
| GET | `/v0/vendor_reviews/{id}` | Get one vendor review. | path: `id: int` | `Vendor_Reviews` |
| GET | `/v0/vendor_reviews/user_id/{user_id}` | Reviews authored by a user (reviewer). | path: `user_id: int` | `Vendor_Reviews[]` |
| GET | `/v0/vendor_reviews/vendor_user_id/{vendor_user_id}` | Reviews about a given vendor user. | path: `vendor_user_id: int` | `Vendor_Reviews[]` |
| POST | `/v0/vendor_reviews/` | Create a vendor review. | body: `Vendor_Reviews` | `Vendor_Reviews` |
| PUT | `/v0/vendor_reviews/{id}` | Update a vendor review. | path: `id`; body: `Vendor_Reviews` | `Vendor_Reviews` |
| DELETE | `/v0/vendor_reviews/{id}` | Delete a vendor review. | path: `id: int` | `{ deleted: true }` |

## `/v0/vendor_types` — Vendor specialty/type lookup

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/vendor_types/` | List all vendor types. | none | `Vendor_Types[]` |
| GET | `/v0/vendor_types/{id}` | Get one vendor type. | path: `id: int` | `Vendor_Types` |
| POST | `/v0/vendor_types/` | Create a vendor type. | body: `Vendor_Types` | `Vendor_Types` |
| PUT | `/v0/vendor_types/{id}` | Update a vendor type. | path: `id`; body: `Vendor_Types` | `Vendor_Types` |
| DELETE | `/v0/vendor_types/{id}` | Delete a vendor type. | path: `id: int` | `{ deleted: true }` |

## `/v0/vendors` — Vendor profiles (contractor companies)

| Method | Path | Description | Input | Output |
|---|---|---|---|---|
| GET | `/v0/vendors/` | List all vendors. | none | `Vendors[]` |
| GET | `/v0/vendors/{id}` | Get one vendor by id. | path: `id: int` | `Vendors` |
| GET | `/v0/vendors/vendor_user_id/{vendor_user_id}` | Get vendor by underlying `user_id`. | path: `vendor_user_id: int` | `Vendors` |
| POST | `/v0/vendors/` | Create a vendor profile. | body: `Vendors` | `Vendors` |
| PUT | `/v0/vendors/{id}` | Update a vendor profile. | path: `id`; body: `Vendors` | `Vendors` |
| DELETE | `/v0/vendors/{id}` | Delete a vendor profile. | path: `id: int` | `{ deleted: true }` |

