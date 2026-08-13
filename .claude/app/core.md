# InspectlyAI Backend Core Reference

`app/core/` holds the cross-cutting infrastructure and the major feature engines that the API layer depends on. This document walks each module in order.

```
app/core/
├── config.py           # Pydantic Settings (env vars)
├── database.py         # psycopg2 connection / context manager
├── security.py         # API-key auth dependency
├── common/             # shared infra (S3, LLM framework, observability, model registry)
│   ├── aws_operations.py
│   ├── framework/pydantic/model_provider.py
│   ├── llm_observability/pydantic_logfire/instrument_logfire.py
│   └── models/{open_ai,types}.py
├── property_report_extract/   # LLM pipeline that extracts issues + images from inspection PDFs
│   ├── issue_extract.py       # orchestrator
│   ├── extract_issue.py       # text → issues
│   ├── extract_image.py       # images → assigned to issues
│   ├── model_provider.py
│   ├── helper.py              # PDF / imgbb / fs utilities
│   ├── constants.py
│   ├── types.py
│   ├── agents/{agents_issue,agents_image}.py   # PydanticAI agent definitions
│   └── prompts/prompts.py
└── stripe/             # checkout sessions + webhook for offer payments
    ├── stripe_session.py
    ├── stripe_webhook.py
    ├── serializer.py
    └── types.py
```

---

## Infrastructure

### `config.py` — Pydantic Settings singleton

Loads env vars from `.env` at import time via `pydantic_settings.BaseSettings`.

- `Settings` (config.py:4-39): declares every required env var. Computed `DATABASE_URL` builds the Postgres connection string from `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD`.
- `get_settings()` (config.py:35-37): `@lru_cache()`'d accessor — singleton.
- `settings` (config.py:39): module-level instance everything else imports.

Env vars consumed:
- **DB:** `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- **API:** `API_STR`, `V0_STR`, `PROJECT_NAME`
- **Auth:** `INSPECTLYAI_API_KEY`
- **Frontend:** `FRONTEND_BASE_URL`
- **Stripe:** `STRIPE_SECRET_KEY`, `STRIPE_PUBLIC_KEY`, `STRIPE_WEBHOOK_SECRET`
- **Observability:** `LOGFIRE_API_KEY`
- **AWS:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- **Image hosting:** `IMGBB_API_KEY`, `IMGBB_API_URL`

Missing env vars raise at import time — there's no lazy validation.

### `database.py` — psycopg2 context manager

- `get_db_cursor()` (database.py:10-36): async context manager. Opens a new psycopg2 connection using `settings.*`, yields a `RealDictCursor` (rows as dicts), commits on clean exit, rolls back on exception, always closes in `finally`.
- `test_connection()` (database.py:38-45): runs `SELECT 1`, returns bool. Used by `/db_status`.

Used by ~30+ CRUD modules with the pattern `with get_db_cursor() as cursor: cursor.execute(...)`.

**Gotchas:**
- No connection pooling — every CRUD call opens a fresh connection.
- Queries in many CRUD modules are string-formatted rather than parameterized (SQL injection surface).

### `security.py` — API-key dependency

- `api_key_header` (security.py:10): `APIKeyHeader(name='InspectlyAI-API-Key', auto_error=False)`.
- `get_api_key()` (security.py:12-18): async FastAPI dependency. Compares the incoming `InspectlyAI-API-Key` header against `os.getenv('InspectlyAI-API-Key')`; raises `HTTPException(403)` on mismatch.

Wired in via `Depends(get_api_key)` (e.g. `app/api/runner.py:8`).

**Gotchas:**
- Calls `load_dotenv(override=True)` (security.py:8) even though `config.py` already loaded the env — a second load with override.
- Uses `os.getenv` rather than `settings.INSPECTLYAI_API_KEY` (the env-var literal `InspectlyAI-API-Key` is the canonical name here).
- Plain string compare — no constant-time comparison, no rate limiting.

---

## `common/` — shared infrastructure

### `common/aws_operations.py`

`AWS_Operations` (aws_operations.py): thin async wrapper around `app.utils.s3.S3` for property-report PDFs.

- `upload_file(user_id, listing_id, name, property_report)`: uploads bytes to bucket `inspectly-ai-property-reports`; filename derived via `app.utils.helpers.get_file_unique_name()`.
- `download_file(bucket_name, object_name)`: fetches an object.

Imported by `app/api/v0/endpoints/reports.py:9` but the actual upload call is currently commented out in the extract-issues endpoint (reports.py:55-56). Backed by aiobotocore via the underlying `S3` class, using `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`.

### `common/framework/pydantic/model_provider.py`

`IModelProvider` Protocol — defines the contract for anything that hands a PydanticAI agent its model + settings.

- `get_model(**kwargs) -> models.Model`
- `get_model_settings(**kwargs) -> ModelSettings`

Implemented concretely in `property_report_extract/model_provider.py`. Used as a type hint in the agent classes so the pipeline can swap providers without touching agent code.

### `common/llm_observability/pydantic_logfire/instrument_logfire.py`

Class decorator that wires [Logfire](https://logfire.pydantic.dev/) telemetry into any class that uses LLMs.

- `Instrument_Type` enum: `PANDANTIC_AI = 'pydantic_ai'` (sic — typo on `PANDANTIC`), `OPENAI = 'openai'`.
- `@instrument_logfire(instrument_type, project, use_class_name=False)`: wraps `__init__` to:
  - call `logfire.configure(token=LOGFIRE_API_KEY, service_name=..., scrubbing=False, local=True)`
  - call `logfire.instrument_pydantic_ai()` or `logfire.instrument_openai()` per the enum
  - attach a `self.logfire` handle (with `.info`, `.error`, `.span`) to the instance

Service name = `project` + 5-char UUID prefix (or class name if `use_class_name=True`). Applied to `IssueExtract` (issue_extract.py:13).

**Gotchas:**
- Logfire is reconfigured every time a decorated class is instantiated.
- PII scrubbing is disabled (`scrubbing=False`).
- Loads `.env` again with `override=True`.

### `common/models/types.py` + `common/models/open_ai.py` — model registry

`types.py` defines the catalog shape:
- `Provider` enum: `openai`, `anthropic`, `google`.
- `ReasoningEffort` enum: `low`, `medium`, `high`.
- `Settings`: `allow_temperature`, `allow_reasoning_effort`, `reasoning_effort` defaults.
- `Models`: `model_name`, `provider`, `model_settings` — one entry per supported model.

`open_ai.py` instantiates `OpenAIModels` with constants for each model: `gpt_4_1_mini`, `gpt_5`, `gpt_5_mini`, `gpt_5_1`, `gpt_5_4_mini`, `gpt_5_5`, `o3`, `o3_mini`, `o4_mini`. Each carries the right `Settings` so the `ModelProvider` can only ask for parameters that model actually supports.

Used heavily by `property_report_extract/`:
- `extract_issue.py:22` → `OpenAIModels.gpt_5_5` for the main issue-extract agents
- `agents/agents_issue.py:24` (issue type classifier) and the entire `agents/agents_image.py` → `OpenAIModels.gpt_5_4_mini`
- `property_report_extract/model_provider.py:15-16` → defaults: primary `gpt_5_5`, fallback `gpt_4_1_mini`

---

## `property_report_extract/` — LLM issue + image extraction pipeline

The core intelligence engine: takes a property inspection PDF and produces structured `Issue` rows with classified types and CDN-hosted images. Runs as a FastAPI background task after the report upload endpoint.

### Pipeline flow

```
POST /v0/reports/extract/issues  (reports.py:41-75)
   │
   ├─► create Reports row → report_id
   ├─► create Tasks row (task_type = EXTRACT_ISSUES) → task_id
   └─► BackgroundTasks → IssueExtract(...).run()
                              │
                              ├─► ExtractIssues.extract_issues()             [text]
                              │     1. issues_extract_agent   (gpt-5.5, high)  → all issues
                              │     2. issues_verifier_agent  (gpt-5.5, high)  → fill omissions
                              │     3. issue_type_agent       (gpt-5.4-mini)   → classify each (parallel)
                              │
                              ├─► ExtractImage.extract_images(issues)        [vision]
                              │     1. PyMuPDF extracts embedded images + per-page screenshots
                              │     2. For each image (parallel):
                              │          image_description_agent → 1-2 sentence description
                              │          image_classifier_agent  → is_issue? (filters logos/etc.)
                              │          upload to imgbb → CDN url
                              │     3. image_extractor_agent → map image → issue id (parallel)
                              │     4. image_verifier_agent  → validate + clean per issue (parallel)
                              │
                              ├─► persist each Issue via crud.issues.create()
                              ├─► update Task status → COMPLETED (or FAILED on error)
                              └─► delete tmp/data/output/{task_id}/
```

`extract_issue.py` is the text pipeline. `extract_image.py` is the vision pipeline. `issue_extract.py` is the orchestrator that calls both and persists results.

### `constants.py`

- `MAX_PDF_BYTES` = 20 MB (informational only; not enforced anywhere)
- `MIN_IMAGE_SIZE` = 100 KB (filters out thumbnails/logos when extracting embedded images)
- `SCREENSHOT_ZOOM` = 1 (zoom factor for `fitz` page screenshots)
- `DATA_OUTPUT_FOLDER` = `tmp/data/output` (temp scratch space; cleaned after each task)

### `types.py`

- `IssueTypes` enum (types.py:6-16): `ROOFING`, `EXTERIOR`, `STRUCTURE`, `ELECTRICAL`, `HEATING`, `COOLING`, `INSULATION`, `PLUMBING`, `INTERIOR`, `OTHER` — the classification ontology.
- `Issue` (types.py:18-24): `id`, `name`, `description`, `images: list[str]` (filenames), `imgbb_urls: list[str]`, `type: IssueTypes`.
- `ReportIssues` (types.py:26-27): wrapper `{ issues: List[Issue] }` — extractor output type.
- `ImageClassification` (types.py:29-31): `is_issue: bool`, `reason: str`.

### `model_provider.py`

`ModelProvider` implements `IModelProvider`. Builds a `FallbackModel(primary=gpt_5_5, fallback=gpt_4_1_mini)` so a primary-model outage doesn't kill the pipeline. `get_model_settings(high_effort=True)` returns `OpenAIResponsesModelSettings(temperature=0.0, reasoning_effort='high')`. Reads `OPENAI_API_KEY` from env.

### `helper.py` — PDF + image utilities

- `extract_images_from_pdf(pdf_file, output_folder, logfire)` (helper.py:25-68): uses `fitz` (PyMuPDF) to pull embedded images from each page. CMYK → RGB conversion; drops anything under `MIN_IMAGE_SIZE`. Returns metadata list `[{page_number, image_index_on_page, overall_index, filepath, filename}]`.
- `screenshot_pdf_pages(pdf_file, output_folder, logfire, zoom)` (helper.py:70-99): rasterizes each PDF page to PNG. Screenshots are passed to the image-extractor agent as page-level context.
- `upload_image_to_imgbb(image_file_path, logfire)` (helper.py:101-116): POSTs to imgbb (`IMGBB_API_URL` + `IMGBB_API_KEY`), returns the hosted CDN URL or `None` on failure.
- `delete_images_and_screenshots(task_id)` (helper.py:118-123): async cleanup of `tmp/data/output/{task_id}/`.
- `write_issues_to_json(issues, filepath)` (helper.py:17-23): JSON dump helper (used for debugging).

### `extract_issue.py` — text pipeline

`ExtractIssues` runs the issue text-extraction stages. Agents created via `agents_issue.Agents` with `gpt_5_5` + high reasoning, except the type classifier which uses `gpt_5_4_mini` for cost/speed.

1. `issues_extract_agent` (extract_issue.py:28-32) — PDF in, `ReportIssues` out.
2. `issues_verifier_agent` (extract_issue.py:35-40) — given the first pass + PDF, add anything missing. Does **not** edit existing items.
3. `issue_type_agent` (extract_issue.py:54-68) — per-issue type classification, run in parallel via `asyncio.gather()`.
4. `issue_validator_agent` and `issue_type_validator_agent` are scaffolded but **disabled** (extract_issue.py:42-52, 70-86). The single-pass verifiers carry the QA load.

### `extract_image.py` — vision pipeline

`ExtractImage` is the multimodal half. All agents use `gpt_5_4_mini` + high reasoning.

- `_extract_images_screenshots_metadata()` (extract_image.py:31-34) — calls `helper.extract_images_from_pdf` + `helper.screenshot_pdf_pages`.
- `_process_single_image(image)` (extract_image.py:62-70) — per-image: describe → classify → if issue-related, upload to imgbb. Parallelized across all extracted images (extract_image.py:141-143).
- `_assign_image_to_issue(image, screenshot_data, issues)` (extract_image.py:72-86) — `image_extractor_agent` is shown the **page screenshot** (so it sees the image in its report context), the image bytes, the description, and the full issues list. Returns an `Issue` whose `id` field tells which issue this image belongs to. Parallel.
- `_verify_single_issue(...)` (extract_image.py:88-133) — `image_verifier_agent` sees an issue along with every image assigned to it (paired with each image's page screenshot) and is allowed to drop wrong assignments and clean up the description.
- `extract_images(issues)` (extract_image.py:135-209) — the orchestrator method; cleanup happens in `finally`.

### `issue_extract.py` — orchestrator

`IssueExtract` (issue_extract.py:13) — decorated with `@instrument_logfire(...)`, takes report_id, listing_id, report_name, PDF bytes, task_id.

`run()` (issue_extract.py:34-68):
1. `_extract_issues()` → text pipeline
2. `_extract_images(issues)` → vision pipeline
3. For each issue, calls `crud.issues.create(Issues(...))` with backslashes in `name` and `description` replaced with `-` (issue_extract.py:46-47).
4. Updates the `Tasks` row to `COMPLETED` on success, `FAILED` on any exception.

**Note:** the backslash→hyphen substitution is lossy — issue names from reports often use `"CATEGORY \\ Subcategory"` as a separator and the `\\` gets flattened on insert.

### `agents/agents_issue.py` (5 agents) and `agents/agents_image.py` (4 agents)

These are thin classes that construct PydanticAI `Agent` objects bound to system prompts (from `prompts/prompts.py`) and an output type. The pipelines instantiate one `Agents` per stage. Models per agent are summarized in the table below.

### `prompts/prompts.py`

Long-form prompts (~960 lines). Each agent has a paired `*_SYSTEM_PROMPT` and `*_USER_PROMPT`. Highlights:

- **`ISSUES_EXTRACT_*`** (prompts.py:41-224) — extract every issue from a report verbatim; preserve labels (Condition / Implication(s) / Location / Task / Recommendation / Estimated Cost), don't paraphrase, don't dedupe ambiguous matches.
- **`ISSUES_VERIFIER_*`** (prompts.py:227-331) — additive only: carry candidates forward verbatim, append omissions, preserve order.
- **`ISSUE_VALIDATION_*`** (prompts.py:334-469) — disabled in code; per-issue restoration of missing labels.
- **`ISSUE_TYPE_*`** (prompts.py:472-614) — strict component-first ontology with precedence (ROOFING > EXTERIOR > STRUCTURE > ELECTRICAL > … > OTHER). Output must be one of the 10 UPPERCASE tokens.
- **`IMAGE_DESCRIPTION_*`** (prompts.py:757-795) — neutral 1-2 sentence description (component + location + visible condition).
- **`IMAGE_CLASSIFIER_*`** (prompts.py:798-841) — issue-related vs decorative; signals for each.
- **`IMAGE_EXTRACTOR_*`** (prompts.py:844-887) — map image → issue id given page screenshot + issues list.
- **`IMAGE_VERIFIER_*`** (prompts.py:890-963) — QA per issue: drop mismatched images, optionally clean description.

### Agent summary

| Agent | Stage | Model | Output |
|---|---|---|---|
| `issues_extract_agent` | text | `gpt-5.5` (high) | `ReportIssues` |
| `issues_verifier_agent` | text | `gpt-5.5` (high) | `ReportIssues` |
| `issue_type_agent` | text | `gpt-5.4-mini` (high) | `str` (one `IssueTypes` token) |
| `issue_validator_agent` | text | `gpt-5.5` (high) | `Issue` — *disabled* |
| `issue_type_validator_agent` | text | `gpt-5.5` (high) | `str` — *disabled* |
| `image_description_agent` | vision | `gpt-5.4-mini` (high) | `str` |
| `image_classifier_agent` | vision | `gpt-5.4-mini` (high) | `ImageClassification` |
| `image_extractor_agent` | vision | `gpt-5.4-mini` (high) | `Issue` (with `id`) |
| `image_verifier_agent` | vision | `gpt-5.4-mini` (high) | `Issue` |

### Env vars

- `OPENAI_API_KEY` — model access (model_provider.py:17)
- `IMGBB_API_URL`, `IMGBB_API_KEY` — issue-image CDN (helper.py:101-116)
- `LOGFIRE_API_KEY` — observability (via `@instrument_logfire`)

### Notable behavior / gotchas

- **Heavy parallelism** in the image pipeline — `asyncio.gather()` on describe/classify/upload, on image→issue mapping, and on per-issue verification.
- **FallbackModel** — every agent silently falls back to `gpt-4.1-mini` if the primary fails mid-call.
- **Verbatim text** — pipeline is explicitly designed to preserve the inspector's wording. The backslash→hyphen substitution in `issue_extract.py:46-47` is the one exception.
- **100 KB image filter** discards small embedded images (logos, separators) before they ever reach an LLM.
- **Temp files** live under `tmp/data/output/{task_id}/` and are deleted in the `finally` block; cleanup failures are logged but don't fail the task.
- **No retry / dedup** at the pipeline level — if `run()` is invoked twice for the same task, you'll get duplicate issues in the DB.
- **Logfire scrubbing is off** (see common/llm_observability) — report contents end up in traces.

---

## `stripe/` — checkout sessions & webhooks for offer payments

Handles the payment leg of the vendor-offer workflow: client picks a vendor's offer on an issue, pays via Stripe Checkout, and on success the system marks that offer accepted, rejects all competing offers, and moves the issue to `in_progress` with the winning vendor assigned.

### `types.py`

- `Checkout_Session_Request` (types.py:5-8): `{ client_id, vendor_id, offer_id }`.
- `Checkout_Session_Response` (types.py:10-12): `{ session_id, url }`.
- `Stripe_Checkout_Session` enum (types.py:14-18): the four webhook event types handled — `checkout.session.completed`, `checkout.session.async_payment_succeeded`, `checkout.session.async_payment_failed`, `checkout.session.expired`.

### `stripe_session.py` — checkout creation

`stripe.api_key` set at import time from `settings.STRIPE_SECRET_KEY` (stripe_session.py:7).

`Stripe_Session.checkout_session(data)` (stripe_session.py:13-44):
1. Validates client (must have a row in `user_stripe_information`), vendor, and offer via `serializer.py`.
2. Creates a Stripe Checkout Session:
   - **Mode:** one-time payment (no subscriptions).
   - **Currency:** CAD, hardcoded (stripe_session.py:22). Price = `int(round(offer['price'] * 100))`.
   - **Product name:** `"Payment for offer #{offer_id}"`.
   - **Customer:** the client's existing Stripe customer id.
   - **Payment methods:** card only.
   - **Success URL:** frontend issue page with `?payment=success&session_id={SESSION_ID}`.
   - **Cancel URL:** same page with `?payment=failed`.
   - **Metadata:** `{ offer_id, client_id, vendor_id }` (stripe_session.py:36-40) — this is what the webhook reads back.
3. Returns `(session.url, session)`. Stripe API errors are wrapped in `RuntimeError`.

### `stripe_webhook.py` — event handling

Webhook signing secret from `settings.STRIPE_WEBHOOK_SECRET` (stripe_webhook.py:19).

- `_validate_webhook(payload, stripe_signature)` (stripe_webhook.py:21-32): `stripe.Webhook.construct_event(...)`; raises `ValueError` on bad signature/payload.
- `webhook(payload, stripe_signature)` (stripe_webhook.py:34-70):
  - **Success path** (`COMPLETED` / `PAYMENT_SUCCEEDED`):
    1. `validate_webhook_metadata(session)` extracts and re-checks `(offer_id, client_id, vendor_id, offer, issue, issue_id)`.
    2. Fetch all offers on the issue.
    3. Winning offer → `Bid_Status.ACCEPTED`; every other not-yet-terminal offer → `Bid_Status.REJECTED`. Each update also stamps `user_last_viewed = utcnow()`.
    4. Issue updated: `vendor_id` set, `status = Status.IN_PROGRESS`.
  - **Failure path** (`PAYMENT_FAILED` / `EXPIRED`): logged only, no DB writes — the offer stays `received` and is still actionable.
  - **Anything else:** returns "unhandled".

### `serializer.py` — validation helpers

- `validate_user(user_id)` (serializer.py:12-24): loads the user's `stripe_user_id`; `LookupError` if missing.
- `validate_issue_offer(offer_id)` (serializer.py:26-47): checks the offer exists, isn't already accepted/rejected, and that its issue + report exist; enriches the offer dict with `report_id` and `listing_id`.
- `validate_webhook_metadata(session)` (serializer.py:49-74): pulls the three IDs back out of the Checkout Session metadata and verifies vendor matches the offer, and the issue still exists.

All three raise `LookupError` / `ValueError` which the API layer maps to 404 / 400.

### API integration

Exposed in `app/api/v0/endpoints/stripe.py`, mounted at `/v0/stripe` (`runner_v0.py:63`):
- `POST /checkout/create-session` → `Stripe_Session().checkout_session(...)`.
- `POST /checkout/webhook` → `Stripe_Webhook().webhook(payload, stripe_signature)`. The raw request body must be read with `await request.body()` so the signature verification works against unparsed bytes.

Stripe-customer provisioning lives in `app/crud/stripe_user_information.py::create_stripe_existing_user()` — call that for any user before they can pay.

### Env vars

- `STRIPE_SECRET_KEY` — Stripe SDK auth
- `STRIPE_WEBHOOK_SECRET` — webhook signature verification
- `STRIPE_PUBLIC_KEY` — declared in `Settings` but not used in the backend
- `FRONTEND_BASE_URL` — embedded in success/cancel redirects

### Notable behavior / gotchas

- **Atomic offer state machine on success** — exactly one offer accepted, the rest rejected, all in the webhook handler.
- **No idempotency** — Stripe retries can re-run the success path; nothing in the handler deduplicates against `event.id` or session id. Reprocessing is mostly safe (idempotent updates) but offer-update timestamps will move and any concurrent state change is unprotected.
- **No payment ledger** — Stripe charge id, amount, and event id are not persisted to the app DB. The webhook updates offer + issue rows and that's it; audit trail lives only in Stripe.
- **Currency is hardcoded to CAD.**
- **Stripe customer prerequisite** — `validate_user` fails if the client isn't already in `user_stripe_information`. Stripe customers are not auto-created at signup.
- **Failure events are silent** — `PAYMENT_FAILED` and `EXPIRED` don't change any DB state; the offer remains `received` indefinitely.
- **Non-transactional DB updates in the webhook** — offer updates and the issue update aren't wrapped in a single transaction; a mid-flight failure can leave the offer `ACCEPTED` while the issue stays `OPEN`.
