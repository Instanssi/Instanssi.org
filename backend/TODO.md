# V2 API Implementation Status

This document tracks the implementation status of the REST API v2 endpoints for all Django models in the Instanssi backend.

## Access Level Legend

- **Anonymous**: No authentication required
- **Authenticated**: Requires login (any authenticated user)
- **Owner**: Requires login, access limited to own data only
- **Staff**: Requires Django model permissions (add/change/delete/view)
- **Infodesk**: Requires `store.change_storetransaction` permission

---

## Django Model Permissions Reference

Django auto-generates these permissions for each model. Staff access in the v2 API requires these permissions.

### Kompomaatti App (`kompomaatti`)

| Model | View | Add | Change | Delete |
|-------|------|-----|--------|--------|
| Event | `kompomaatti.view_event` | `kompomaatti.add_event` | `kompomaatti.change_event` | `kompomaatti.delete_event` |
| Profile | `kompomaatti.view_profile` | `kompomaatti.add_profile` | `kompomaatti.change_profile` | `kompomaatti.delete_profile` |
| VoteCodeRequest | `kompomaatti.view_votecoderequest` | `kompomaatti.add_votecoderequest` | `kompomaatti.change_votecoderequest` | `kompomaatti.delete_votecoderequest` |
| TicketVoteCode | `kompomaatti.view_ticketvotecode` | `kompomaatti.add_ticketvotecode` | `kompomaatti.change_ticketvotecode` | `kompomaatti.delete_ticketvotecode` |
| Compo | `kompomaatti.view_compo` | `kompomaatti.add_compo` | `kompomaatti.change_compo` | `kompomaatti.delete_compo` |
| Entry | `kompomaatti.view_entry` | `kompomaatti.add_entry` | `kompomaatti.change_entry` | `kompomaatti.delete_entry` |
| AlternateEntryFile | `kompomaatti.view_alternateentryfile` | `kompomaatti.add_alternateentryfile` | `kompomaatti.change_alternateentryfile` | `kompomaatti.delete_alternateentryfile` |
| VoteGroup | `kompomaatti.view_votegroup` | `kompomaatti.add_votegroup` | `kompomaatti.change_votegroup` | `kompomaatti.delete_votegroup` |
| Vote | `kompomaatti.view_vote` | `kompomaatti.add_vote` | `kompomaatti.change_vote` | `kompomaatti.delete_vote` |
| Competition | `kompomaatti.view_competition` | `kompomaatti.add_competition` | `kompomaatti.change_competition` | `kompomaatti.delete_competition` |
| CompetitionParticipation | `kompomaatti.view_competitionparticipation` | `kompomaatti.add_competitionparticipation` | `kompomaatti.change_competitionparticipation` | `kompomaatti.delete_competitionparticipation` |

### Store App (`store`)

| Model | View | Add | Change | Delete |
|-------|------|-----|--------|--------|
| StoreItem | `store.view_storeitem` | `store.add_storeitem` | `store.change_storeitem` | `store.delete_storeitem` |
| StoreItemVariant | `store.view_storeitemvariant` | `store.add_storeitemvariant` | `store.change_storeitemvariant` | `store.delete_storeitemvariant` |
| StoreTransaction | `store.view_storetransaction` | `store.add_storetransaction` | `store.change_storetransaction` | `store.delete_storetransaction` |
| StoreTransactionEvent | `store.view_storetransactionevent` | `store.add_storetransactionevent` | `store.change_storetransactionevent` | `store.delete_storetransactionevent` |
| TransactionItem | `store.view_transactionitem` | `store.add_transactionitem` | `store.change_transactionitem` | `store.delete_transactionitem` |
| Receipt | `store.view_receipt` | `store.add_receipt` | `store.change_receipt` | `store.delete_receipt` |

### Programme App (`ext_programme`)

| Model | View | Add | Change | Delete |
|-------|------|-----|--------|--------|
| ProgrammeEvent | `ext_programme.view_programmeevent` | `ext_programme.add_programmeevent` | `ext_programme.change_programmeevent` | `ext_programme.delete_programmeevent` |

### Blog App (`ext_blog`)

| Model | View | Add | Change | Delete |
|-------|------|-----|--------|--------|
| BlogEntry | `ext_blog.view_blogentry` | `ext_blog.add_blogentry` | `ext_blog.change_blogentry` | `ext_blog.delete_blogentry` |

### Archive App (`arkisto`)

| Model | View | Add | Change | Delete |
|-------|------|-----|--------|--------|
| OtherVideoCategory | `arkisto.view_othervideocategory` | `arkisto.add_othervideocategory` | `arkisto.change_othervideocategory` | `arkisto.delete_othervideocategory` |
| OtherVideo | `arkisto.view_othervideo` | `arkisto.add_othervideo` | `arkisto.change_othervideo` | `arkisto.delete_othervideo` |

### Upload App (`admin_upload`)

| Model | View | Add | Change | Delete |
|-------|------|-----|--------|--------|
| UploadedFile | `admin_upload.view_uploadedfile` | `admin_upload.add_uploadedfile` | `admin_upload.change_uploadedfile` | `admin_upload.delete_uploadedfile` |

### Django Auth (`auth`)

| Model | View | Add | Change | Delete |
|-------|------|-----|--------|--------|
| User | `auth.view_user` | `auth.add_user` | `auth.change_user` | `auth.delete_user` |

---

## V1 API Reference

The v1 API provides these endpoints (for reference when implementing v2):

### Public Endpoints (no auth required)
- `GET /api/v1/events/` - List events (filtered to Instanssi events)
- `GET /api/v1/competitions/` - List active competitions
- `GET /api/v1/competition_participations/` - List participations (active competitions only)
- `GET /api/v1/compos/` - List active compos
- `GET /api/v1/compo_entries/` - List entries (voting started or archived)
- `GET /api/v1/programme_events/` - List active programme events
- `GET /api/v1/store_items/` - List available store items (supports `secret_key` param)
- `POST /api/v1/store_transaction/` - Create store transaction (anonymous checkout)

### User Endpoints (IsAuthenticated)
- `GET/POST/PUT/DELETE /api/v1/user_entries/` - User's own compo entries
- `GET/POST/PUT/DELETE /api/v1/user_participations/` - User's own competition participations
- `GET/POST /api/v1/user_vote_codes/` - User's own ticket vote codes
- `GET/POST/PUT /api/v1/user_vote_code_requests/` - User's own vote code requests
- `GET/POST /api/v1/user_votes/` - User's own votes (VoteGroup)
- `GET /api/v1/current_user/` - Current user info

### Admin Endpoints (IsAdminUser + DjangoModelPermissions)
- `GET /api/v1/admin/events/` - All events (read-only)
- `GET /api/v1/admin/compos/` - All compos (read-only)
- `GET /api/v1/admin/compo_entries/` - All entries (read-only)

### Other v1 Endpoints
- `GET /api/v1/ics/instanssi.ics` - iCal feed for programme events

---

## Kompomaatti App (`Instanssi/kompomaatti/models.py`)

### Event

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x]  | [ ]    | [ ]    | [ ]    | - |
| Authenticated | [x] | [ ]   | [ ]    | [ ]    | - |
| Staff       | [x]  | [x]    | [x]    | [x]    | `kompomaatti.{view,add,change,delete}_event` |

**v2 Status:**
- [x] v2 API implemented (`/api/v2/events/`)
- [x] Public read access for all events
- [x] Staff-only write operations

**v1 Reference:**
- v1 filters to events with name starting with "Instanssi"
- v2 returns all events (more flexible)

### Compo

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x] (active only) | [ ] | [ ] | [ ] | - |
| Authenticated | [x] (active only) | [ ] | [ ] | [ ] | - |
| Staff       | [x] (all)         | [x] | [x] | [x] | `kompomaatti.{view,add,change,delete}_compo` |

**v2 Status:**
- [x] v2 API implemented (`/api/v2/event/<event_pk>/kompomaatti/compos/`)
- [x] Public read access for active compos
- [x] Staff can see/manage inactive compos
- [x] Event-scoped via URL parameter

**v1 Reference:**
- Exposes: id, event, name, description, adding_end, editing_end, compo_start, voting_start, voting_end, max_source_size, max_entry_size, max_image_size, source_format_list, entry_format_list, image_format_list, show_voting_results, entry_view_type, is_votable, is_imagefile_allowed, is_imagefile_required

### Entry (Compo Entry)

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x] (voting started) | [ ] | [ ] | [ ] | - |
| Authenticated | [x] (voting started) | [ ] | [ ] | [ ] | - |
| Owner       | [x]  | [x]    | [x]    | [x]    | IsAuthenticated (own entries only) |
| Staff       | [x]  | [x]    | [x]    | [x]    | `kompomaatti.{view,add,change,delete}_entry` |

**v2 Status:**
- [x] v2 API implemented (staff: `/api/v2/event/<event_pk>/kompomaatti/entries/`)
- [x] v2 API implemented (user: `/api/v2/event/<event_pk>/user/kompomaatti/entries/`)
- [x] Public read access after voting has started
- [x] Users can manage their own entries during adding/editing period
- [x] Time-based restrictions enforced (adding_end, editing_end)
- [ ] File upload validation (formats, size limits) - v1 has full validation
- [ ] Copy entryfile to imagefile when compo.is_imagefile_copied is True

**v1 Reference:**
- Public serializer hides file URLs until voting started or show_voting_results
- User serializer validates file formats, sizes, and compo deadlines
- Includes `alternate_files` in response (AlternateEntryFile nested)

### AlternateEntryFile

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x] (nested) | [ ] | [ ] | [ ] | - |
| Authenticated | [x] (nested) | [ ] | [ ] | [ ] | - |
| Staff       | [x]  | [x]    | [x]    | [x]    | `kompomaatti.{view,add,change,delete}_alternateentryfile` |

**v2 Status:**
- [ ] v2 API not implemented
- [ ] Auto-generated from Entry via Celery tasks
- [ ] Should be nested read-only in Entry response (v1 does this)

**v1 Reference:**
- Nested in CompoEntrySerializer with fields: format (mime_format), url

### Competition

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x] (active only) | [ ] | [ ] | [ ] | - |
| Authenticated | [x] (active only) | [ ] | [ ] | [ ] | - |
| Staff       | [x] (all)         | [x] | [x] | [x] | `kompomaatti.{view,add,change,delete}_competition` |

**v2 Status:**
- [x] v2 API implemented (`/api/v2/event/<event_pk>/kompomaatti/competitions/`)
- [x] Public read access for active competitions
- [x] Staff can see/manage inactive competitions
- [x] Event-scoped via URL parameter

### CompetitionParticipation

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x] (after start) | [ ]  | [ ]  | [ ]  | - |
| Authenticated | [x] (after start) | [ ]  | [ ]  | [ ]  | - |
| Owner       | [x]  | [x]    | [x]    | [x]    | IsAuthenticated (own participations only) |
| Staff       | [x]  | [x]    | [x]    | [x]    | `kompomaatti.{view,add,change,delete}_competitionparticipation` |

**v2 Status:**
- [x] v2 API implemented (staff: `/api/v2/event/<event_pk>/kompomaatti/competition_participations/`)
- [x] Public read access after competition has started
- [x] v2 User API for managing own participations (`/api/v2/event/<event_pk>/user/kompomaatti/participations/`)

**v1 Reference:**
- Public serializer hides score/rank/disqualified until show_results is True
- User endpoint validates: competition active, participation_end not passed, no duplicate participation
- User can create/update/delete own participations

### VoteCodeRequest

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Authenticated | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Owner       | [x]  | [x]    | [x]    | [ ]    | IsAuthenticated (own requests only) |
| Staff       | [x]  | [x]    | [x]    | [x]    | `kompomaatti.{view,add,change,delete}_votecoderequest` |

**v2 Status:**
- [x] v2 API implemented (staff: `/api/v2/event/<event_pk>/kompomaatti/vote_code_requests/`)
- [x] v2 User API for own requests (`/api/v2/event/<event_pk>/user/kompomaatti/vote_code_requests/`)

**v1 Reference:**
- User endpoint: create, read, update (no delete)
- Status field: 0=Pending, 1=Accepted, 2=Rejected (read-only for users)
- Validates: no duplicate request per event

### TicketVoteCode

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Authenticated | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Owner       | [x]  | [x]    | [ ]    | [ ]    | IsAuthenticated (own codes only) |
| Staff       | [x]  | [x]    | [x]    | [x]    | `kompomaatti.{view,add,change,delete}_ticketvotecode` |

**v2 Status:**
- [x] v2 API implemented (staff: `/api/v2/event/<event_pk>/kompomaatti/ticket_vote_codes/`)
- [x] v2 User API for associating codes (`/api/v2/event/<event_pk>/user/kompomaatti/ticket_vote_codes/`)

**v1 Reference:**
- User endpoint: create, read only (no update/delete)
- User provides `ticket_key` (partial key), system finds matching TransactionItem
- Validates: key not already used, key exists and is paid ticket, no duplicate per event

### VoteGroup

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Authenticated | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Owner       | [x]  | [x]    | [ ]    | [ ]    | IsAuthenticated (own votes only) |
| Staff       | [x]  | [x]    | [x]    | [x]    | `kompomaatti.{view,add,change,delete}_votegroup` |

**v2 Status:**
- [x] v2 User API implemented (`/api/v2/event/<event_pk>/user/kompomaatti/votes/`)

**v1 Reference:**
- User endpoint: create, read only
- Create with: compo, entries (list of entry IDs in vote order)
- Validates: compo voting is open, user has voting rights (TicketVoteCode or approved VoteCodeRequest), entries belong to compo, no duplicate entries
- Creating for same compo replaces existing votes

### Vote

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Authenticated | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Staff       | [x]  | [x]    | [x]    | [x]    | `kompomaatti.{view,add,change,delete}_vote` |

**v2 Status:**
- [ ] v2 API not implemented
- [ ] Managed through VoteGroup, probably doesn't need direct API

### Profile

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Authenticated | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Owner       | [x]  | [ ]    | [x]    | [ ]    | IsAuthenticated (own profile only) |
| Staff       | [x]  | [x]    | [x]    | [x]    | `kompomaatti.{view,add,change,delete}_profile` |

**v2 Status:**
- [ ] v2 API not implemented
- [ ] No v1 API exists
- [ ] Contains `otherinfo` field (contact info like IRC nick)

---

## Store App (`Instanssi/store/models.py`)

### StoreItem

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x] (available) | [ ] | [ ] | [ ] | - |
| Authenticated | [x] (available) | [ ] | [ ] | [ ] | - |
| Staff       | [x]  | [x]    | [x]    | [x]    | `store.{view,add,change,delete}_storeitem` |

**v2 Status:**
- [ ] v2 Public API not implemented (public read, secret_key support)
- [ ] v2 Staff API not implemented (`/api/v2/event/<event_pk>/store/items/`)

**v1 Reference:**
- Public read-only, no auth required
- Filters: available=True, max>0
- Supports `secret_key` query param to show hidden items
- Includes nested `variants` (StoreItemVariant)
- Fields: id, event, name, description, price, max, available, imagefile_original_url, imagefile_thumbnail_url, max_per_order, sort_index, discount_amount, discount_percentage, is_discount_available, discount_factor, num_available, variants

### StoreItemVariant

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x] (nested) | [ ] | [ ] | [ ] | - |
| Authenticated | [x] (nested) | [ ] | [ ] | [ ] | - |
| Staff       | [x]  | [x]    | [x]    | [x]    | `store.{view,add,change,delete}_storeitemvariant` |

**v2 Status:**
- [ ] v2 API not implemented (nested in StoreItem response)
- [ ] v2 Staff API not implemented (`/api/v2/event/<event_pk>/store/item_variants/`)

### StoreTransaction

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [ ]  | [x]    | [ ]    | [ ]    | - (checkout only) |
| Authenticated | [ ]  | [x]    | [ ]    | [ ]    | - (checkout only) |
| Owner       | [x] (by key) | [ ] | [ ] | [ ] | - (own transactions via key) |
| Infodesk    | [x]  | [ ]    | [x]    | [ ]    | `store.change_storetransaction` |
| Staff       | [x]  | [x]    | [x]    | [x]    | `store.{view,add,change,delete}_storetransaction` |

**v2 Status:**
- [ ] v2 Public API not implemented (anonymous checkout)
- [ ] v2 Staff API not implemented (`/api/v2/event/<event_pk>/store/transactions/`)

**v1 Reference:**
- Write-only endpoint (POST only), no auth required
- Creates transaction and returns payment URL
- Input: first_name, last_name, company, email, telephone, mobile, street, postal_code, city, country, information, payment_method, read_terms, items (list of {item_id, variant_id, amount}), save (boolean)
- Validates: terms accepted, items available, payment method valid

**Infodesk Access (HTML views):**
- Search transactions by name/key
- View transaction details
- Mark items as delivered
- Requires `store.change_storetransaction` permission

### StoreTransactionEvent

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Authenticated | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Staff       | [x]  | [ ]    | [ ]    | [ ]    | `store.view_storetransactionevent` |

**v2 Status:**
- [ ] v2 Staff API not implemented (`/api/v2/event/<event_pk>/store/transaction_events/`) - read-only audit log

### TransactionItem

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x] (by key) | [ ] | [ ] | [ ] | - (ticket view by key) |
| Authenticated | [x] (by key) | [ ] | [ ] | [ ] | - (ticket view by key) |
| Infodesk    | [x]  | [ ]    | [x]    | [ ]    | `store.change_storetransaction` |
| Staff       | [x]  | [x]    | [x]    | [x]    | `store.{view,add,change,delete}_transactionitem` |

**v2 Status:**
- [ ] v2 Staff API not implemented (`/api/v2/event/<event_pk>/store/transaction_items/`)

**Current Access:**
- HTML view by item key (`/store/ti/<key>/`) - shows ticket/item details
- Infodesk can mark as delivered
- Contains `key` field used for ticket verification

### Receipt

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Authenticated | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Staff       | [x]  | [ ]    | [ ]    | [ ]    | `store.view_receipt` |

**v2 Status:**
- [ ] v2 Staff API not implemented (`/api/v2/event/<event_pk>/store/receipts/`) - read-only audit

---

## Programme App (`Instanssi/ext_programme/models.py`)

### ProgrammeEvent

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x] (active) | [ ] | [ ] | [ ] | - |
| Authenticated | [x] (active) | [ ] | [ ] | [ ] | - |
| Staff       | [x]  | [x]    | [x]    | [x]    | `ext_programme.{view,add,change,delete}_programmeevent` |

**v2 Status:**
- [ ] v2 Public API not implemented (public read active)
- [ ] v2 Staff API not implemented (`/api/v2/event/<event_pk>/programme/events/`)
- [ ] iCal feed endpoint

**v1 Reference:**
- Public read-only
- Filters: active=True
- Also available as iCal feed: `/api/v1/ics/instanssi.ics`

---

## Blog App (`Instanssi/ext_blog/models.py`)

### BlogEntry

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x] (public) | [ ] | [ ] | [ ] | - |
| Authenticated | [x] (public) | [ ] | [ ] | [ ] | - |
| Staff       | [x]  | [x]    | [x]    | [x]    | `ext_blog.{view,add,change,delete}_blogentry` |

**v2 Status:**
- [x] v2 API implemented (`/api/v2/blog_entries/`)
- [ ] Should filter to public=True for anonymous users (currently shows all?)

**Other Access:**
- RSS feed: `/blog/rss/` - public entries only

---

## Archive App (`Instanssi/arkisto/models.py`)

### OtherVideoCategory

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x] (archived events) | [ ] | [ ] | [ ] | - |
| Authenticated | [x] (archived events) | [ ] | [ ] | [ ] | - |
| Staff       | [x]  | [x]    | [x]    | [x]    | `arkisto.{view,add,change,delete}_othervideocategory` |

**v2 Status:**
- [ ] v2 Public API not implemented (public read for archived events)
- [ ] v2 Staff API not implemented (`/api/v2/event/<event_pk>/archive/video_categories/`)

**Current Access (HTML views):**
- Shown on archived event pages
- Event-scoped

### OtherVideo

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [x] (archived events) | [ ] | [ ] | [ ] | - |
| Authenticated | [x] (archived events) | [ ] | [ ] | [ ] | - |
| Staff       | [x]  | [x]    | [x]    | [x]    | `arkisto.{view,add,change,delete}_othervideo` |

**v2 Status:**
- [ ] v2 Public API not implemented (public read for archived events)
- [ ] v2 Staff API not implemented (`/api/v2/event/<event_pk>/archive/videos/`)

**Current Access:**
- HTML view: `/arkisto/video/<id>/`
- Only for archived events
- Contains YouTube URL

---

## Archive JSON API (Non-REST)

The arkisto app has JSON endpoints that could be migrated to v2:

- `GET /arkisto/<event_id>/json/` - Returns entries and compos for archived event
  - Fields: id, compo_name, compo_id, entry_name, entry_author, entry_score, entry_rank, entry_result_url, entry_source_url, entry_youtube_url, entry_image_thumbnail, entry_image_medium, entry_image_original

- `GET /arkisto/<event_id>/entries.m3u8` - M3U8 playlist of audio entries (WEBM alternates)

- `GET /arkisto/<event_id>/results.txt` - Plain text results

---

## Upload App (`Instanssi/admin_upload/models.py`)

### UploadedFile

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Authenticated | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Staff       | [x]  | [x]    | [x]    | [x]    | `admin_upload.{view,add,change,delete}_uploadedfile` |

**v2 Status:**
- [ ] v2 Staff API not implemented (`/api/v2/event/<event_pk>/uploads/`) - file management for event graphics etc.

---

## User Management (Django Auth)

### User

| Access Level | Read | Create | Update | Delete | Required Permission |
|-------------|------|--------|--------|--------|---------------------|
| Anonymous   | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Authenticated | [ ]  | [ ]    | [ ]    | [ ]    | - |
| Owner       | [x] (self) | [ ] | [x] (self) | [ ] | IsAuthenticated (self only) |
| Staff       | [x]  | [x]    | [x]    | [x]    | `auth.{view,add,change,delete}_user` |

**v2 Status:**
- [x] v2 API implemented (staff: `/api/v2/users/`)
- [x] v2 API implemented (self: `/api/v2/user_info/`)
- [ ] User self-update (password change, email, etc.)

**v1 Reference:**
- `/api/v1/current_user/` - Read-only, returns id, first_name, last_name, email

---

## Authentication

**v2 Status:**
- [x] Social auth URLs (`/api/v2/auth/social_urls/`)
- [x] Login endpoint (`/api/v2/auth/login/`)
- [x] Logout endpoint (`/api/v2/auth/logout/`)
- [ ] Password reset endpoint
- [ ] Email verification endpoint
- [ ] Account registration endpoint

---

## Permission Patterns Reference

### Common Permission Classes

```python
# Full Django model permissions (view/add/change/delete)
class FullDjangoModelPermissions(DjangoModelPermissions):
    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": ["%(app_label)s.view_%(model_name)s"],
        "HEAD": ["%(app_label)s.view_%(model_name)s"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

# Public read + staff write pattern
class ActiveItemReadPermission(FullDjangoModelPermissions):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)

# Infodesk access (store.change_storetransaction)
def infodesk_access_required(view_func):
    # Checks user.has_perm("store.change_storetransaction")
```

### v1 Admin Permissions
```python
class AdminViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser, DjangoModelPermissions]
```

---

## Summary

### Fully Implemented in v2
- [x] Event (public read, staff write)
- [x] Compo (public read active, staff write)
- [x] Entry/CompoEntry (public read after voting, user/staff write)
- [x] Competition (public read active, staff write)
- [x] CompetitionParticipation (public read after start, staff write)
- [x] VoteCodeRequest (staff only)
- [x] TicketVoteCode (staff only)
- [x] BlogEntry (staff only - needs public filter)
- [x] User (staff only)
- [x] UserInfo (self read)
- [x] Authentication (login/logout/social)

### Needs User-Level v2 API (exists in v1) - **ALL COMPLETE**
- [x] UserCompetitionParticipation - user's own participations (`/api/v2/event/<event_pk>/user/kompomaatti/participations/`)
- [x] UserVoteCodeRequest - user's own vote code requests (`/api/v2/event/<event_pk>/user/kompomaatti/vote_code_requests/`)
- [x] UserTicketVoteCode - user's own vote codes (`/api/v2/event/<event_pk>/user/kompomaatti/ticket_vote_codes/`)
- [x] UserVoteGroup - user's own votes (`/api/v2/event/<event_pk>/user/kompomaatti/votes/`)

### Not Implemented in v2 (exists in v1)
- [ ] StoreItem - public read, nested variants
- [ ] StoreTransaction - anonymous create for checkout
- [ ] ProgrammeEvent - public read active, iCal feed
- [ ] CurrentUser - self info (partially covered by user_info)

### Needs Staff/Management v2 API
- [ ] StoreItem (`/api/v2/event/<event_pk>/store/items/`)
- [ ] StoreItemVariant (`/api/v2/event/<event_pk>/store/item_variants/`)
- [ ] StoreTransaction (`/api/v2/event/<event_pk>/store/transactions/`)
- [ ] StoreTransactionEvent (`/api/v2/event/<event_pk>/store/transaction_events/`) - read-only
- [ ] TransactionItem (`/api/v2/event/<event_pk>/store/transaction_items/`)
- [ ] Receipt (`/api/v2/event/<event_pk>/store/receipts/`) - read-only
- [ ] ProgrammeEvent (`/api/v2/event/<event_pk>/programme/events/`)
- [ ] OtherVideoCategory (`/api/v2/event/<event_pk>/archive/video_categories/`)
- [ ] OtherVideo (`/api/v2/event/<event_pk>/archive/videos/`)
- [ ] UploadedFile (`/api/v2/event/<event_pk>/uploads/`)

### Not Implemented in v2 (no v1 equivalent)
- [ ] Profile - user profile management
- [ ] AlternateEntryFile - nested in Entry response
- [ ] Vote - managed via VoteGroup
- [ ] Archive JSON API - entry/compo data for archived events

---

## Implementation Priority

### High Priority (Core User Functionality)
1. **User-specific Kompomaatti APIs:** ✅ **ALL COMPLETE**
   - [x] UserCompetitionParticipation
   - [x] UserVoteCodeRequest
   - [x] UserTicketVoteCode
   - [x] UserVoteGroup (voting)

2. **Store API (enables web store):**
   - [ ] StoreItem (public read, nested variants)
   - [ ] StoreItem (staff CRUD)
   - [ ] StoreItemVariant (staff CRUD)
   - [ ] StoreTransaction (anonymous create for checkout)
   - [ ] StoreTransaction (staff CRUD)
   - [ ] TransactionItem (staff CRUD)

### Medium Priority (Event Features)
1. **Programme API:**
   - [ ] ProgrammeEvent (public read active)
   - [ ] ProgrammeEvent (staff CRUD)
   - [ ] iCal feed endpoint

2. **Archive API:**
   - [ ] OtherVideoCategory (public read, staff CRUD)
   - [ ] OtherVideo (public read, staff CRUD)
   - [ ] Archive JSON endpoint migration

3. **Entry Improvements:**
   - [ ] AlternateEntryFile nested in response
   - [ ] Full file validation in UserCompoEntry

### Low Priority (Admin/Internal)
1. **Profile management:**
   - [ ] Profile API

2. **Admin/Staff APIs:**
   - [ ] UploadedFile (staff CRUD)
   - [ ] StoreTransactionEvent (staff read-only audit)
   - [ ] Receipt (staff read-only audit)

3. **Infodesk API:**
   - [ ] Transaction search/view
   - [ ] Item delivery marking

---

## URL Structure

### Current v2 Structure
```
/api/v2/
├── events/
├── users/
├── blog_entries/
├── auth/
│   ├── social_urls/
│   ├── login/
│   └── logout/
├── user_info/
└── event/<event_pk>/
    ├── kompomaatti/
    │   ├── compos/
    │   ├── entries/
    │   ├── competitions/
    │   ├── competition_participations/
    │   ├── vote_code_requests/
    │   └── ticket_vote_codes/
    └── user/
        └── kompomaatti/
            ├── entries/
            ├── participations/
            ├── vote_code_requests/
            ├── ticket_vote_codes/
            └── votes/
```

### Proposed Additions
```
/api/v2/
└── event/<event_pk>/
    ├── store/                          # Staff CRUD + public read
    │   ├── items/
    │   ├── item_variants/
    │   ├── transactions/
    │   ├── transaction_items/
    │   ├── transaction_events/         # Read-only audit
    │   └── receipts/                   # Read-only audit
    ├── programme/
    │   └── events/                     # Staff CRUD + public read
    ├── archive/
    │   ├── videos/                     # Staff CRUD + public read
    │   └── video_categories/           # Staff CRUD + public read
    └── uploads/                        # Staff CRUD only
```

---

## Testing Patterns

### Test Directory Structure

Tests follow two patterns:

1. **Simple endpoints** (staff-only with no special logic): Single file
   ```
   tests/api/v2/
   ├── test_events.py        # All access level tests in one file
   ├── test_blog_entries.py
   └── test_users.py
   ```

2. **Complex endpoints** (multiple access levels, special logic): Directory with access-level files
   ```
   tests/api/v2/kompomaatti/compos/
   ├── test_staff.py          # Staff with permissions - full CRUD
   ├── test_unauthenticated.py # Anonymous users - public read
   └── test_unauthorized.py    # Logged in without permissions
   ```

3. **User-owned endpoints**: Different naming
   ```
   tests/api/v2/kompomaatti/user_compo_entries/
   ├── test_authorized.py      # Authenticated user managing own data
   └── test_unauthenticated.py # Anonymous users (401)
   ```

### Test Fixtures (from `tests/conftest.py` and `tests/api/conftest.py`)

**API Clients:**
- `api_client` - Unauthenticated REST client
- `auth_client` - Authenticated as `base_user` (no special permissions)
- `user_api_client` - Authenticated as `normal_user` (no special permissions)
- `staff_api_client` - Authenticated as `staff_user` (has kompomaatti.* permissions)
- `super_api_client` - Authenticated as `super_user` (superuser, all permissions)

**Users:**
- `base_user` - Basic user, no permissions
- `normal_user` - Basic user with `is_staff=False`
- `staff_user` - Staff user with kompomaatti permissions
- `super_user` - Superuser with all permissions

**Model Fixtures:**
- `event` - Base event for testing
- `open_compo`, `votable_compo`, `closed_compo`, `inactive_compo` - Compos in different states
- `editable_compo_entry`, `votable_compo_entry`, `closed_compo_entry` - Entries in different states
- `competition`, `started_competition`, `inactive_competition` - Competitions in different states
- `competition_participation`, `started_competition_participation` - Participations
- `vote_code_request`, `ticket_vote_code` - Voting-related fixtures
- `store_item`, `hidden_item`, `variant_item`, `discount_item` - Store items
- `store_transaction`, `transaction_item_*` - Store transactions
- File fixtures: `entry_zip`, `source_zip`, `image_png` (and variants `*2`)

### Test Patterns

**1. Parameterized access tests (quick coverage):**
```python
@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),   # Public read access
        ("POST", 401),  # Create denied
        ("PUT", 401),   # Update denied
        ("PATCH", 401), # Partial update denied
        ("DELETE", 401),# Delete denied
    ],
)
def test_unauthenticated_list(api_client, event, method, status):
    base_url = get_base_url(event.id)
    assert api_client.generic(method, base_url).status_code == status
```

**2. Detailed CRUD tests (staff):**
```python
@pytest.mark.django_db
def test_staff_can_create(staff_api_client, event):
    req = staff_api_client.post(base_url, {...})
    assert req.status_code == 201
    assert req.data["field"] == expected_value
```

**3. Time-based restriction tests (user endpoints):**
```python
@pytest.mark.django_db
def test_cannot_create_after_deadline(auth_client, closed_compo):
    req = auth_client.post(base_url, {...})
    assert req.status_code == 400
    assert "deadline" in str(req.data).lower()
```

**4. Visibility tests (public read with conditions):**
```python
@pytest.mark.django_db
def test_anonymous_cannot_see_inactive(api_client, inactive_compo):
    req = api_client.get(f"{base_url}{inactive_compo.id}/")
    assert req.status_code == 404

@pytest.mark.django_db
def test_staff_can_see_inactive(staff_api_client, inactive_compo):
    req = staff_api_client.get(f"{base_url}{inactive_compo.id}/")
    assert req.status_code == 200
```

**5. Field visibility tests (hidden until condition):**
```python
@pytest.mark.django_db
def test_public_cannot_see_score_before_results(api_client, participation):
    participation.competition.show_results = False
    participation.competition.save()
    req = api_client.get(f"{base_url}{participation.id}/")
    assert req.data["score"] is None
```

---

## Test Coverage Status

### Implemented Tests

#### Event-scoped Staff APIs
| Endpoint | Unauthenticated | Unauthorized | Staff | Notes |
|----------|----------------|--------------|-------|-------|
| `/api/v2/events/` | [x] | [x] | [x] | Single file pattern |
| `/api/v2/event/<id>/kompomaatti/compos/` | [x] | [x] | [x] | Directory pattern, inactive visibility |
| `/api/v2/event/<id>/kompomaatti/entries/` | [x] | [x] | [x] | Directory pattern |
| `/api/v2/event/<id>/kompomaatti/competitions/` | [x] | [x] | [x] | Directory pattern, inactive visibility |
| `/api/v2/event/<id>/kompomaatti/competition_participations/` | [x] | [x] | [x] | Time-based visibility, score/rank hiding |
| `/api/v2/event/<id>/kompomaatti/vote_code_requests/` | [x] | [x] | [x] | Directory pattern |
| `/api/v2/event/<id>/kompomaatti/ticket_vote_codes/` | [x] | [x] | [x] | Directory pattern |

#### User-owned APIs
| Endpoint | Unauthenticated | Authorized | Notes |
|----------|----------------|------------|-------|
| `/api/v2/event/<id>/user/kompomaatti/entries/` | [x] | [x] | Time-based restrictions, file uploads, inactive compo handling |
| `/api/v2/event/<id>/user/kompomaatti/participations/` | [x] | [x] | Time-based restrictions, duplicate prevention, inactive competition handling |
| `/api/v2/event/<id>/user/kompomaatti/vote_code_requests/` | [x] | [x] | Duplicate prevention, status read-only for users |
| `/api/v2/event/<id>/user/kompomaatti/ticket_vote_codes/` | [x] | [x] | Ticket key validation, paid transaction check |
| `/api/v2/event/<id>/user/kompomaatti/votes/` | [x] | [x] | Voting rights check, time-based, ranked voting |

#### Other APIs
| Endpoint | Tests | Notes |
|----------|-------|-------|
| `/api/v2/blog_entries/` | [x] | Single file |
| `/api/v2/users/` | [x] | Single file |
| `/api/v2/user_info/` | [x] | Single file |
| `/api/v2/auth/login/` | [x] | |
| `/api/v2/auth/logout/` | [x] | |
| `/api/v2/auth/social_urls/` | [x] | |

### Tests Needed for New Endpoints

#### High Priority: User-owned Kompomaatti APIs - **ALL COMPLETE**

**UserCompetitionParticipation** (`/api/v2/event/<id>/user/kompomaatti/participations/`) - **COMPLETE**
- [x] `test_unauthenticated.py` - All methods return 401
- [x] `test_authorized.py`:
  - [x] Create participation in active competition
  - [x] Read own participations
  - [x] Update own participation
  - [x] Delete own participation
  - [x] Cannot create after `participation_end`
  - [x] Cannot create duplicate participation
  - [x] Cannot access inactive competition
  - [x] Only sees own participations (not others')

**UserVoteCodeRequest** (`/api/v2/event/<id>/user/kompomaatti/vote_code_requests/`) - **COMPLETE**
- [x] `test_unauthenticated.py` - All methods return 401
- [x] `test_authorized.py`:
  - [x] Create vote code request
  - [x] Read own requests
  - [x] Update own request (text only, not status)
  - [x] Cannot delete requests
  - [x] Cannot create duplicate request per event
  - [x] Status field is read-only for users
  - [x] Only sees own requests

**UserTicketVoteCode** (`/api/v2/event/<id>/user/kompomaatti/ticket_vote_codes/`) - **COMPLETE**
- [x] `test_unauthenticated.py` - All methods return 401
- [x] `test_authorized.py`:
  - [x] Associate ticket key to account (create)
  - [x] Read own vote codes
  - [x] Cannot update or delete
  - [x] Key validation (must exist, must be paid, must be ticket)
  - [x] Cannot use already-associated key
  - [x] Cannot create duplicate per event
  - [x] Only sees own codes

**UserVoteGroup/Votes** (`/api/v2/event/<id>/user/kompomaatti/votes/`) - **COMPLETE**
- [x] `test_unauthenticated.py` - All methods return 401
- [x] `test_authorized.py`:
  - [x] Create votes during voting period
  - [x] Read own votes
  - [x] Voting rights validation (TicketVoteCode or approved VoteCodeRequest)
  - [x] Cannot vote outside voting period
  - [x] Entries must belong to specified compo
  - [x] No duplicate entries in vote
  - [x] Replacing existing votes for same compo

#### High Priority: Store APIs

**StoreItem** (`/api/v2/store/items/`)
- [ ] `test_unauthenticated.py`:
  - [ ] Can read available items
  - [ ] Cannot see unavailable items
  - [ ] Cannot see items with max=0
  - [ ] Hidden items accessible with `secret_key` param
  - [ ] Variants nested in response
  - [ ] Cannot create/update/delete
- [ ] `test_staff.py`:
  - [ ] Full CRUD with permissions

**StoreTransaction** (`/api/v2/store/transactions/`)
- [ ] `test_unauthenticated.py`:
  - [ ] Can create transaction (checkout)
  - [ ] Cannot read transactions
  - [ ] Validates items exist and available
  - [ ] Validates payment method
  - [ ] Validates terms accepted
  - [ ] Returns payment URL on success
- [ ] `test_owner.py`:
  - [ ] Can read own transaction by key (if implemented)

#### Medium Priority

**ProgrammeEvent** (`/api/v2/programme/events/`)
- [ ] `test_unauthenticated.py`:
  - [ ] Can read active events
  - [ ] Cannot see inactive events
  - [ ] Proper filtering by event
- [ ] `test_staff.py`:
  - [ ] Full CRUD with permissions

**OtherVideoCategory** (`/api/v2/archive/categories/`)
- [ ] `test_unauthenticated.py`:
  - [ ] Can read categories for archived events
- [ ] `test_staff.py`:
  - [ ] Full CRUD with permissions

**OtherVideo** (`/api/v2/archive/videos/`)
- [ ] `test_unauthenticated.py`:
  - [ ] Can read videos for archived events
  - [ ] Proper YouTube URL handling
- [ ] `test_staff.py`:
  - [ ] Full CRUD with permissions

#### Low Priority

**Profile** (`/api/v2/user/profile/`)
- [ ] `test_unauthenticated.py` - Returns 401
- [ ] `test_authorized.py`:
  - [ ] Read own profile
  - [ ] Update own profile
  - [ ] Cannot see others' profiles

**UploadedFile** (`/api/v2/admin/files/`)
- [ ] `test_unauthenticated.py` - Returns 401
- [ ] `test_unauthorized.py` - Returns 403
- [ ] `test_staff.py`:
  - [ ] Full CRUD with `admin_upload.*` permissions

### Endpoint-Specific Test Considerations

| Endpoint | Special Considerations |
|----------|----------------------|
| Compos | Test `active` flag visibility; staff sees all, public sees active only |
| Entries | Test voting_start visibility; file URL hiding until voting; time-based edit restrictions |
| Competitions | Test `active` flag visibility |
| CompetitionParticipation | Test `start` time visibility; `show_results` affects score/rank visibility |
| UserCompoEntries | File uploads (multipart/form-data); time restrictions (adding_end, editing_end); compo.active filtering |
| UserParticipations | Time restrictions (participation_end); duplicate prevention |
| UserVoteCodeRequest | Status field read-only for users; duplicate prevention per event |
| UserTicketVoteCode | Key validation against TransactionItem; already-used key check |
| UserVotes | Voting rights check; voting period check; entry validation |
| StoreItem | secret_key query param; nested variants; availability filtering |
| StoreTransaction | Payment integration; item validation; complex nested input |
