# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## Project Overview

This is the Django backend for Instanssi.org, a Finnish demoparty event management system. The codebase manages:
- **Kompomaatti**: Compo (competition) submissions, voting, and results
- **Store**: Event ticket and merchandise sales with Paytrail payment integration
- **Archive**: Historical event and entry data
- **Programme**: Event schedules and programme management
- **Admin panels**: Event management interfaces for organizers
- **APIs**: REST APIs (v1 and v2) with DRF Spectacular for OpenAPI docs

## Development Commands

### ⚠️ REQUIRED: After Adding or Modifying Code

**You MUST run these tools after making any code changes:**

```bash
make check
```

This will run pytest in parallel, black, isort and django-manage checks.

These checks are mandatory before considering any task complete. Do not skip them.

### Setup
```bash
# Install dependencies (requires Poetry and Python 3.13+)
make env

# Copy settings template and configure
cp settings.py-dist settings.py
# Edit settings.py with your configuration (never commit this file)

# Run migrations
make migrate

# Create superuser
make create-admin

# Start development server
make start-server

# Start celery worker (for background tasks)
make start-celery
```

### Testing
```bash
# Run all tests
make pytest

# Run with coverage
make coverage

# Run tests in parallel (auto-detects CPU cores)
make pytest-parallel

# Run specific test file
poetry run pytest tests/store/test_models.py
```

## Architecture

### Project Structure

- **Instanssi/**: Main Django project directory
  - **kompomaatti/**: Core compo system (Entry, Compo, Vote, Competition models)
  - **store/**: E-commerce (StoreItem, StoreTransaction, TransactionItem, Receipt)
  - **arkisto/**: Archive of past events and entries
  - **users/**: User authentication and profiles
  - **api/**: REST APIs with v1 (legacy) and v2 (current) versions
  - **ext_\***: External integrations (ext_blog, ext_mastodon, ext_programme)
  - **main20XX/**: Year-specific landing pages
  - **infodesk/**: Infodesk/ticket validation interface
  - **common_config.py**: Shared Django settings
  - **settings.py**: Local configuration (never committed)

### Key Models and Relationships

**Kompomaatti (competition system):**
- `Event` → Contains `Compo` and `Competition` objects
- `Compo` → Has multiple `Entry` objects (user submissions)
- `Entry` → Can have `Vote` objects and `AlternateEntryFile` (transcoded media)
- `Vote` → Grouped by `VoteGroup` per user/compo
- `TicketVoteCode` → Links store tickets to voting rights
- `Competition` → Has `CompetitionParticipation` (for non-submission contests)

**Store (e-commerce):**
- `StoreItem` → Can have `StoreItemVariant` (sizes, colors, etc.)
- `StoreTransaction` → Contains multiple `TransactionItem` objects
- `TransactionItem` → Individual purchased items with unique keys (for tickets)
- `Receipt` → Email receipts for transactions
- Ticket items can be used as `TicketVoteCode` for voting rights

**Cross-cutting:**
- Events are the central organizing concept
- Store tickets link to kompomaatti voting via `TicketVoteCode`
- User model is Django's built-in auth User

### Settings Architecture

Configuration is split across multiple files:
- `common_config.py`: Shared base configuration (middleware, apps, templates)
- `settings.py`: Local overrides (database, secrets, API keys) - **never committed**
- `settings.py-dist`: Template for local settings
- `test_settings.py`: Test-specific configuration

Helper functions in `common_config.py`:
- `make_celery_conf()`: Redis broker config
- `make_cache_conf()`: Local memory (dev) or Redis (prod) cache
- `make_email_conf()`: Console (dev) or SMTP (prod) email
- `setup_sentry()`: Sentry error tracking integration

### Background Tasks

Celery is used for async tasks:
- `Instanssi/celery.py`: Celery app configuration
- `Instanssi/kompomaatti/tasks.py`: Entry media transcoding (audio formats)
- `Instanssi/store/tasks.py`: Store-related background jobs
- Redis is the message broker (required for production)

### Static Assets

- Static files are in `Instanssi/static/` and per-app `static/` directories
- SCSS is compiled via django-libsass
- Assets are compressed with django-compressor (offline compression in production)

### Payment Integration

Store uses Paytrail API v2 for payment processing:
- Configuration: `PAYTRAIL_V2_ID`, `PAYTRAIL_V2_SECRET`, `PAYTRAIL_V2_API_URL`
- Handlers in `Instanssi/store/handlers.py`
- API docs available in `docs/paytrail-api.yaml`

### Media File Handling

Media files are organized by type in `content/uploads/`:
- `MEDIA_COMPO_ENTRIES`: Entry submission files
- `MEDIA_COMPO_SOURCES`: Entry source code
- `MEDIA_COMPO_IMAGES`: Entry thumbnail images
- `MEDIA_COMPO_ALTERNATES`: Transcoded audio files
- `MEDIA_STORE_IMAGES`: Store product images
- `MEDIA_PROGRAMME_IMAGES`: Programme images
- `MEDIA_UPLOAD_FILES`: General uploads

Files are auto-organized with timestamps and cleaned filenames via `common.file_handling` utilities.

### Authentication

Multiple OAuth backends configured via python-social-auth:
- Google OAuth2
- GitHub OAuth2
- Steam OpenID
- Django's built-in ModelBackend

Login URL for users is `/users/login/`.

### REST API

Two API versions:
- **APIv1**: Legacy endpoints under `/api/v1/`
- **APIv2**: Current endpoints under `/api/v2/` with OpenAPI docs via drf-spectacular

Authentication:
- Knox token authentication (64-char tokens, 7-day TTL, 3 tokens per user)
- Session authentication (for browsable API)

Access OpenAPI schema at `/api/v2/schema/` (when served).

### Testing

Test fixtures are defined in `tests/conftest.py` with comprehensive factories for:
- Users (base, normal, staff, super)
- Events, Compos, Competitions
- Entries and Votes
- Store items, transactions, and receipts
- Authenticated test clients

Tests use pytest-django with:
- Automatic test database setup
- Temporary media root for file uploads
- Faker for realistic test data
- freezegun for time-based testing

**Test Style:**

- Do not use test classes. Write tests as plain functions (`def test_something():`, not `class TestSomething:`).
- Use pytest fixtures for test setup and shared state. Place fixtures in `conftest.py` files.
- Before creating new fixtures, check existing `conftest.py` files for reusable fixtures.
- Prefer the AAA pattern: Arrange, Act, Assert.

**API Testing Requirements:**

When writing tests for API endpoints, you MUST test all three authorization scenarios:
1. **Unauthenticated users** - No credentials provided
2. **Authenticated but unauthorized users** - Valid credentials but lacking required permissions
3. **Authorized users** - Valid credentials with appropriate permissions

Use `pytest.mark.parametrize` when feasible to reduce code duplication and ensure consistent coverage across these scenarios.

## Important Patterns

### Entry File Handling

Entries support alternate formats for browser playback:
- Audio entries are automatically transcoded to web formats (Opus/WebM, AAC/MP4)
- Transcoding triggered by `Entry.generate_alternates()` on save
- Celery tasks handle async conversion via ffmpeg-python

### Voting System

Voting uses ranked-choice within vote groups:
- Users create one `VoteGroup` per compo
- Each `Vote` in the group has a rank (1st, 2nd, 3rd choice, etc.)
- Scores calculated as sum of `1/rank` across all votes
- Voting requires a `TicketVoteCode` (from ticket purchase or manual grant)

### Store Discounts

Quantity-based discounts:
- `discount_amount`: Minimum quantity to trigger discount
- `discount_percentage`: Percent off when threshold reached
- Prices calculated with `Decimal` arithmetic to avoid floating-point errors
- Methods: `get_discounted_unit_price()`, `get_discounted_subtotal()`

### Secret Store Items

Items can be hidden behind secret keys:
- `is_secret=True` hides item from public store listing
- `secret_key`: URL parameter to reveal item (`?secret_key=kissa`)
- Use `StoreItem.items_visible(secret_key)` to query visible items

## URL Structure

- `/2024/`, `/2026/`: Year-specific event landing pages
- `/kompomaatti/`: Public compo browsing and participation
- `/arkisto/`: Historical event archive
- `/store/`: Ticket and merchandise store
- `/api/v1/`, `/api/v2/`: REST APIs
- `/admin/`: Django admin (debug/development only)

Root URL redirects to current year's main page (currently `/2026/`).

Note: The Vue-based admin panel (`/management/`) is deployed separately and served directly by nginx in production.
