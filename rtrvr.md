# Agent API /agent

The primary entry point to the rtrvr.ai planner + tools engine. Send one JSON payload that can browse the web, load tabular data as in-memory sheets, call tools, and return structured results.

Try Playground

Get API Key

Full Planner Engine

Multi-step reasoning with automatic tool orchestration and browser control.

Tabular Data Inputs

Load CSV, JSON, XLSX, or Parquet files as in-memory sheets for enrichment.

Structured Outputs

Define JSON schemas for type-safe, predictable result formats.

New: Run agents from your terminal with [rtrvr CLI](https://www.rtrvr.ai/docs/cli) — `rtrvr run "Extract products" --url https://example.com`

### Agent API Playground

POST

/agent

Planner + tools engine in API mode.

Try:

API Key

Get from [rtrvr.ai/cloud](https://www.rtrvr.ai/cloud?view=api-keys)

Task Description

*

URLs

(one per line)

```
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "input": "Retrieve the top 5 article titles and authors.",
  "urls": [
    "https://news.ycombinator.com/"
  ],
  "response": {
    "verbosity": "final"
  }
}'
```

Base URL

https://api.rtrvr.ai

Primary endpoints: `/agent` (planner + tools) and `/scrape` (raw page data).

Use your API key in the `Authorization` header:

Header

```
Authorization: Bearer rtrvr_your_api_key
```

Security:

Always keep your key on the server side (e.g. backend, serverless). Never embed it in browser code or ship it to clients.

POST

https://api.rtrvr.ai

/agent

Send a single JSON payload describing what you want. The planner orchestrates browser tabs, tools, and in-memory sheets to get the job done.

cURL

```
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Summarize the main points of this page in 5 bullet points.",
    "urls": ["https://example.com/blog/ai-trends-2025"],
    "response": { "verbosity": "final" }
  }'
```

Internally, this maps to an execution trajectory. New requests get a new `trajectoryId`; continuations reuse it.

For low-level raw page data, see the [Scrape API docs](https://www.rtrvr.ai/docs/scrape) (`/scrape`).

Both endpoints share the same browser + proxy infra but are optimized for different jobs.

Dimension

/agent

/scrape

What it does

Full agent run: planner + tools + browser + optional Sheets/Docs/etc.

Loads pages and returns extracted text + accessibility tree.

Typical latency

Higher – dominated by LLM calls and multi-step tools.

Lower – usually just browser + proxy round-trips.

Credits

Infra credits + model/tool credits.

Infra-only credits (browser + proxy); no model/tool usage.

Best for

End-to-end automations, multi-step workflows, writing back to external systems.

Feeding your own LLM/RAG stack, ad-hoc scraping, prefetching page data.

Capabilities

Planner, tools, Sheets workflows, Docs/PDF generation,

ask_user

, etc.

Extracted text, accessibility tree,

elementLinkRecord

, usage metrics.

Before using the Agent API, ensure you have the required setup completed.

### 1. API Key

Get your API key from [rtrvr.ai/cloud → API Keys](https://rtrvr.ai/cloud?view=api-keys)

### 2. Google Integration (Optional)

**Required for:** `generate_sheets`, `generate_docs`, `generate_slides`

1

Sign in to rtrvr.ai/cloud

Go to [rtrvr.ai/cloud](https://rtrvr.ai/cloud) and sign in with your account

2

Connect Google Drive

Click the **Sheets** tab and authorize Google Drive access when prompted

3

Verify Connection

You should see your Google Sheets listed. Try selecting one to confirm access.

**Note:** This is a one-time setup. Once connected, the API will automatically use your Google account for document operations.

### 3. File Uploads (Optional)

To use the `files` parameter, upload files at [rtrvr.ai/cloud → Files](https://rtrvr.ai/cloud?view=files) to get Storage URLs.

### Trajectory & Phase

A **trajectory** is a stable ID for a workflow. Use it to group related phases (e.g. discovery → enrichment → reporting) and continuations.

- Omit `trajectoryId` to start fresh.
- Reuse the same `trajectoryId` with `history.continue = true` to continue.
- `phase` (default `1`) lets you structure long-running projects into multiple stages.

### Planner + Tools

You don't call tools directly. Instead, you describe the task and optionally configure which `enableAdditionalTools` to allow. Support for `tools.enableAdditionalTools` in the public API will come soon.

Under the hood, the planner can call tools like `act_on_tab`, `crawl_and_extract_from_tab`, `sheets_workflow`, `create_sheet_from_data`, and more. Only a subset (Docs, Slides, PDFs, persistent Sheets, ask_user, etc.) is gated behind `enableAdditionalTools` to control cost and latency.

### Tabular Inputs & In-Memory Sheets

Use `dataInputs` to attach CSV/TSV/JSON, text, markdown, or binary formats (XLSX/Parquet via URL or storage). The system:

- Infers the format from extension or content type when omitted.
- Parses header and row schema.
- Creates an in-memory sheet (no Google Drive write) exposed to tools like `sheets_workflow`.

The `files` parameter lets you attach PDFs, images, and documents for the agent to analyze or use. This is different from `dataInputs`which is specifically for tabular/structured data.

What the agent can do with files:

- Read and analyze PDF documents
- Process and describe images (screenshots, diagrams, photos)
- Fill out PDF forms with extracted or provided data
- Upload files to web forms during browser automation
- Compare multiple documents and find differences

### ApiExecuteRequestFile schema

files[].displayName

string

required

Human-readable filename shown to the agent (e.g., 'Q3-Report.pdf', 'screenshot.png')

files[].uri

string

required

File location. Accepts Firebase Storage URL, GCS URI (gs://bucket/path), or public HTTPS URL

files[].mimeType

string

required

MIME type (e.g., 'application/pdf', 'image/png', 'image/jpeg')

### Supported file types

PDF

(

application/pdf

)

PNG

(

image/png

)

JPEG

(

image/jpeg

)

GIF

(

image/gif

)

WebP

(

image/webp

)

Word

(

docx

)

Text

(

text/plain

)

Markdown

(

text/markdown

)

### Three ways to provide file URIs

Recommended

1. Firebase Storage URL

Upload files via [Cloud → Files](https://www.rtrvr.ai/cloud?view=files) and copy the Storage URL. This is the most reliable option.

https://firebasestorage.googleapis.com/v0/b/bucket/o/path%2Ffile.pdf?alt=media&token=...

2. GCS URI

If you have files in Google Cloud Storage, use the gs:// URI directly.

gs://your-bucket/path/to/file.pdf

3. Public HTTPS URL

Any publicly accessible URL. Must not require authentication.

https://example.com/documents/report.pdf

### Example: Analyze a PDF report

PDF Analysis

```
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Extract the key financial metrics from this quarterly report and summarize them.",
    "files": [
      {
        "displayName": "Q3-2024-Report.pdf",
        "uri": "https://firebasestorage.googleapis.com/v0/b/bucket/o/reports%2Fq3.pdf?alt=media&token=abc",
        "mimeType": "application/pdf"
      }
    ],
    "schema": {
      "type": "object",
      "properties": {
        "revenue": { "type": "string" },
        "profit": { "type": "string" },
        "growth": { "type": "string" },
        "highlights": { "type": "array", "items": { "type": "string" } }
      }
    }
  }'
```

### Example: Analyze an image

Image Analysis

```
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Describe this screenshot and identify any UI/UX issues.",
    "files": [
      {
        "displayName": "app-screenshot.png",
        "uri": "gs://my-bucket/screenshots/app-v2.png",
        "mimeType": "image/png"
      }
    ]
  }'
```

### Example: Compare multiple documents

Multi-file comparison

```
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Compare these two contracts and list all the differences.",
    "files": [
      {
        "displayName": "contract-v1.pdf",
        "uri": "https://firebasestorage.googleapis.com/.../contract-v1.pdf?...",
        "mimeType": "application/pdf"
      },
      {
        "displayName": "contract-v2.pdf", 
        "uri": "https://firebasestorage.googleapis.com/.../contract-v2.pdf?...",
        "mimeType": "application/pdf"
      }
    ],
    "schema": {
      "type": "object",
      "properties": {
        "differences": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "section": { "type": "string" },
              "v1_text": { "type": "string" },
              "v2_text": { "type": "string" },
              "significance": { "type": "string" }
            }
          }
        }
      }
    }
  }'
```

### Example: Upload file to web form

File upload during automation

```
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Go to the application page, upload my resume, and fill out the form with name: John Doe, email: john@example.com",
    "urls": ["https://company.com/careers/apply"],
    "files": [
      {
        "displayName": "resume.pdf",
        "uri": "https://firebasestorage.googleapis.com/.../resume.pdf?...",
        "mimeType": "application/pdf"
      }
    ]
  }'
```

Limits & notes:

- Maximum file size: **20MB** per file
- Files are processed by the LLM, larger files may use more credits
- Binary files are base64-encoded internally for LLM processing
- Use `dataInputs` for tabular data (CSV, JSON, Excel) - it's more efficient

The full request shape is `AgentApiRequest`:

AgentApiRequest (conceptual)

```
interface AgentApiRequest {
  // ─────────────────────────────────────────
  // CORE PARAMETERS
  // ─────────────────────────────────────────
  
  /** Stable ID for a workflow. Omit to start new; reuse to continue. */
  trajectoryId?: string;
  
  /** Phase index within a trajectory (default: 1). Use ≥2 for multi-stage workflows. */
  phase?: number;
  
  /** Main user instruction - REQUIRED */
  input: string;
  
  /** URLs to open in browser tabs */
  urls?: string[];
  
  /** JSON Schema describing expected result shape */
  schema?: Schema;

  // ─────────────────────────────────────────
  // FILE INPUTS (PDFs, Images, Documents)
  // ─────────────────────────────────────────
  
  /**
   * File attachments for the agent to process.
   * Supports PDFs, images, and documents up to 20MB each.
   * 
   * The agent can:
   * - Read and analyze file contents
   * - Extract text from PDFs
   * - Analyze images
   * - Upload files to web forms
   */
  files?: ApiExecuteRequestFile[];

  // ─────────────────────────────────────────
  // TABULAR DATA INPUTS
  // ─────────────────────────────────────────
  
  /**
   * Tabular data to load as in-memory sheets.
   * Supports CSV, TSV, JSON, text, markdown, XLSX, Parquet.
   */
  dataInputs?: ApiTabularInput[];

  // ─────────────────────────────────────────
  // TOOL CONFIGURATION
  // ─────────────────────────────────────────
  
  tools?: ApiToolsConfig;

  // ─────────────────────────────────────────
  // SETTINGS & HISTORY
  // ─────────────────────────────────────────
  
  /** Per-request settings override */
  settings?: Partial<UserSettings>;
  
  /** Recording context for guided execution */
  recordingContext?: string;
  
  /** Continuation state from previous runs */
  history?: {
    continue?: boolean;
    previousSteps?: PlannerPreviousStep[];
    lastToolPreviousSteps?: ToolPreviousSteps;
  };

  // ─────────────────────────────────────────
  // RESPONSE CONFIGURATION
  // ─────────────────────────────────────────
  
  response?: {
    /** 'final' (default) | 'steps' | 'debug' */
    verbosity?: ApiVerbosity;
    /** Max bytes for inline output (default: 1MB) */
    inlineOutputMaxBytes?: number;
  };

  // ─────────────────────────────────────────
  // ARTIFACT REUSE (Advanced)
  // ─────────────────────────────────────────
  
  /**
   * Control how the agent reuses existing Google artifacts.
   * Useful for appending to existing Sheets/Docs.
   */
  reuseArtifacts?: ReuseArtifacts;

  // ─────────────────────────────────────────
  // INTERNAL OPTIONS
  // ─────────────────────────────────────────
  
  options?: {
    skipToolsStorageLoad?: boolean;
    pinTools?: boolean;
    pinSettings?: boolean;
    
    /** Execution trigger context */
    trigger?: {
      type: 'schedule' | 'ui' | 'api';
      context?: ScheduleContext;
    };
    
    /** UI and VNC live view settings */
    ui?: {
      /** Enable VNC live browser viewing. Default: false */
      enableVnc?: boolean;
      
      /** 
       * Which browser sessions to expose:
       * - "root": Main browser only (default)
       * - "all": Main + all batch worker browsers
       */
      vncScope?: 'root' | 'all';
      
      /**
       * Emit progress events to Firestore.
       * Opt-in only: set true to enable progress event writes.
       */
      emitEvents?: boolean;
    };
  };

  // ─────────────────────────────────────────
  // WEBHOOKS (Async notifications)
  // ─────────────────────────────────────────

  /**
   * Webhook subscriptions for async delivery of execution results.
   * Up to 5 webhooks per request. Delivered via Cloud Tasks (best-effort).
   */
  webhooks?: WebhookSubscription[];
}

// Webhook subscription type
interface WebhookSubscription {
  /** Webhook endpoint URL (HTTPS required in production) */
  url: string;

  /** Events to subscribe to. If omitted, all events are delivered. */
  events?: (
    | "rtrvr.execution.succeeded"
    | "rtrvr.execution.failed"
    | "rtrvr.execution.cancelled"
    | "rtrvr.execution.requires_input"
  )[];

  /** HTTP method (currently only POST supported) */
  method?: "POST";

  /** Custom headers to include in webhook requests */
  headers?: Record<string, string>;

  /** Authentication config */
  auth?: {
    type: "bearer";
    token: string;
  } | {
    type: "basic";
    username: string;
    password: string;
  };

  /** Secret for HMAC signature (X-Rtrvr-Signature header) */
  secret?: string;

  /** Request timeout in ms (1000-30000, default: 8000) */
  timeoutMs?: number;

  /** Retry policy: "default" (with retries) or "none" */
  retry?: { mode: "default" | "none" };
}

// File input type
interface ApiExecuteRequestFile {
  /** Human-friendly filename, e.g. "Resume-2025.pdf" */
  displayName: string;
  
  /**
   * File location. Accepts:
   * - Firebase Storage URL: https://firebasestorage.googleapis.com/...
   * - GCS URI: gs://bucket/path/to/file
   * - Public HTTPS URL: https://example.com/file.pdf
   */
  uri: string;
  
  /** MIME type, e.g. "application/pdf", "image/png" */
  mimeType: string;
}

// Tabular input type
interface ApiTabularInput {
  /** Optional client-provided correlation ID */
  id?: string;
  
  /** Description for the sheet (used as title) */
  description?: string;
  
  /** Format hint: "csv" | "tsv" | "json" | "text" | "markdown" | "xlsx" | "parquet" */
  format?: InputFormat;
  
  /** Inline data content */
  inline?: string;
  
  /** Remote URL to fetch data from */
  url?: string;
  
  /** Backend storage reference (advanced) */
  storageRef?: StorageReference;
}

// Tools configuration
interface ApiToolsConfig {
  /**
   * Additional tool families to enable.
   * Core tools (browser, extraction, in-memory sheets) are always available.
   */
  enableAdditionalTools?: (
    | "ask_questions"      // Pause for user input
    | "generate_sheets"    // Write to Google Sheets
    | "generate_docs"      // Create Google Docs
    | "generate_slides"      // Create Google Slides
    | "generate_websites"  // Generate web dashboards
    | "generate_pdfs"      // Create new PDFs
    | "pdf_filling"        // Fill PDF forms
  )[];
  
  /** Names of user-defined tools to make available */
  userDefined?: string[];
  
  /**
   * Tool loading mode:
   * - "profile": Load user's saved tools (default)
   * - "allowlist": Only use tools in userDefined
   * - "none": No user-defined tools
   */
  mode?: "allowlist" | "profile" | "none";
}

// Artifact reuse configuration
interface ReuseArtifacts {
  /** 'off' (default) | 'auto' | 'force' */
  mode?: 'off' | 'auto' | 'force';
  
  targets?: {
    sheets?: {
      sheetId: string;
      tabTitle?: string;
      tabId?: number;
      /** 'SAME_TAB' | 'NEW_TAB' */
      tabMode?: 'SAME_TAB' | 'NEW_TAB';
    };
    docs?: {
      docId: string;
      /** 'APPEND' | 'OVERWRITE' */
      mode?: 'APPEND' | 'OVERWRITE';
    };
    slides?: {
      presentationId: string;
      mode?: 'APPEND' | 'OVERWRITE';
    };
    pdfs?: {
      templateFileId?: string;
    };
  };
}
```

### Core fields

input

string

required

Natural-language task description; what you want the system to do.

urls

string[]

Optional list of URLs to open. The first real URL loads full content; others default to text-only for efficiency.

schema

Schema

Optional OpenAPI-style JSON Schema describing the desired final JSON shape. Planner and tools will try to honor it when producing result.json.

trajectoryId

string

Stable ID for a workflow. Omit to start a new trajectory; reuse to continue or add phases.

phase

number

default:

1

Phase index within a trajectory. Use ≥2 for multi-stage workflows.

Example schema: bulleted summary

```
{
  "type": "object",
  "properties": {
    "bullets": {
      "type": "array",
      "items": { "type": "string" }
    },
    "sourceUrl": {
      "type": "string"
    }
  },
  "required": ["bullets"]
}
```

### Tabular inputs (dataInputs)

dataInputs

ApiTabularInput[]

Optional list of tabular inputs to materialize as in-memory sheets.

dataInputs[].description

string

Human-readable description. Used as sheet title in the UI.

dataInputs[].format

"text" | "markdown" | "csv" | "tsv" | "json" | "xlsx" | "parquet"

Optional explicit format. If omitted, inferred from file extension or content type.

dataInputs[].inline

string

Raw content (CSV/TSV/JSON/text/markdown) embedded directly in the request. For XLSX/Parquet prefer URL or storageRef.

dataInputs[].url

string

HTTP(S) URL to fetch as a tabular source (works well for large CSV/XLSX/Parquet files).

dataInputs[].storageRef

StorageReference

Advanced: backend-managed GCS object reference when clients upload to storage directly.

dataInputs example: CSV (inline)

```
# CSV inline
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Enrich each company with website and description.",
    "dataInputs": [
      {
        "description": "Companies",
        "format": "csv",
        "inline": "company\\nOpenAI\\nDeepMind\\nAnthropic\\n"
      }
    ],
    "response": { "verbosity": "steps" }
  }'
```

dataInputs example: JSON (inline)

```
# JSON inline (array of objects)
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Infer seniority and return an updated JSON array.",
    "dataInputs": [
      {
        "description": "Contacts",
        "format": "json",
        "inline": "[{\"name\":\"Alice\",\"title\":\"VP Engineering\"},{\"name\":\"Bob\",\"title\":\"Software Engineer\"}]"
      }
    ],
    "response": { "verbosity": "steps" }
  }'
```

dataInputs example: XLSX (via URL)

```
# XLSX via URL
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Summarize opportunity pipeline from this Excel file.",
    "dataInputs": [
      {
        "description": "Sales pipeline",
        "format": "xlsx",
        "url": "https://example.com/sales-pipeline.xlsx"
      }
    ],
    "response": { "verbosity": "steps" }
  }'
```

dataInputs example: Parquet (via URL)

```
# Parquet via URL
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Compute daily active users per region from this Parquet dataset.",
    "dataInputs": [
      {
        "description": "Events parquet",
        "format": "parquet",
        "url": "https://example.com/events.parquet"
      }
    ],
    "response": { "verbosity": "steps" }
  }'
```

### Tools configuration (tools)

tools.enableAdditionalTools

string[]

Coming soon: optional list of higher-power tool families to enable for this request.

"

ask_questions

"

"

generate_docs

"

"

generate_slides

"

"

generate_websites

"

"

generate_pdfs

"

"

pdf_filling

"

"

generate_sheets

"

Core tools (browser actions, extraction, sheets_workflow on in-memory sheets, etc.) are always enabled. Additional tools control Docs, Slides, PDFs, persistent Sheets, and explicit ask_user behavior.

Google Integration Required

To use `generate_sheets`, `generate_docs`, or `generate_slides`:

1. Sign in at [rtrvr.ai/cloud](https://rtrvr.ai/cloud)
2. Click **Sheets** tab and connect your Google Drive when prompted
3. Verify by checking that you can see and select your Google Sheets

Once connected, the API will use your Google account to create/edit documents.

### Response configuration (response)

response.verbosity

"final" | "steps" | "debug"

default:

"final"

Controls how much detail you get back.

"

final

"

"

steps

"

"

debug

"

response.inlineOutputMaxBytes

number

Hard cap (in bytes) for inline output blocks. Larger payloads are snapshot to storage and previewed.

### History & continuation (history)

history.continue

boolean

Signal that this call should continue a previous workflow state.

history.previousSteps

PlannerPreviousStep[]

Planner-internal state from previous runs. Returned in response.history for advanced clients.

history.lastToolPreviousSteps

ToolPreviousSteps

Tool execution state for the last tool. Used for precise continuations.

### Advanced options

settings

Partial<UserSettings>

Per-request overrides for stored user settings (model, proxy, extraction config, etc.). Generally only needed from first-party or advanced SDKs.

options.skipToolsStorageLoad

boolean

Internal optimization flag when all tools are provided directly. Most clients should omit.

### UI & VNC options (options.ui)

Enable live browser viewing via VNC. Perfect for debugging, demos, or embedding real-time browser sessions in your app.

options.ui.enableVnc

boolean

default:

false

Enable VNC live view for this execution. When true, you can retrieve an embeddable URL to watch the browser in real-time.

options.ui.vncScope

"root" | "all"

default:

"root"

Controls which browser sessions are visible. 'root' shows only the main browser. 'all' includes batch worker browsers when using parallel execution.

"

root

"

"

all

"

options.ui.emitEvents

boolean

default:

false

Opt-in only. When true, execution progress events are written to Firestore for SSE/polling clients. If omitted/false, no execution event stream is written.

emitEvents policy:

API and extension/MCP executions only emit events when

options.ui.emitEvents: true

. CLI streaming defaults on for

run

,

agent

, and

scrape

(use

--no-stream

to disable). Streamed payloads at or under 1MB stay inline; larger payloads include inline preview markers and storage references (`outputRef` / `resultRef` / `responseRef`) for full downloads.

Quick Start:

To embed a live browser view, set

options.ui.enableVnc: true

, then call

POST /vnc/share

to get an iframe-ready URL. See the

VNC Live View section

for full details.

### Webhooks (webhooks)

Get notified when your workflow completes via HTTP webhooks. Up to 5 webhooks per request. Webhooks are delivered asynchronously via Google Cloud Tasks with best-effort delivery and automatic retries.

webhooks[].url

string

required

Webhook endpoint URL. HTTPS required in production. HTTP allowed for localhost development.

webhooks[].events

string[]

Events to subscribe to. If omitted, all events are delivered.

"

rtrvr.execution.succeeded

"

"

rtrvr.execution.failed

"

"

rtrvr.execution.cancelled

"

"

rtrvr.execution.requires_input

"

webhooks[].secret

string

HMAC secret for request signing. If set, requests include X-Rtrvr-Signature header with format: t=timestamp,v1=hmac_sha256

webhooks[].auth

object

Authentication config. Supports Bearer token ({ type: 'bearer', token: '...' }) or Basic auth ({ type: 'basic', username: '...', password: '...' })

webhooks[].headers

Record<string, string>

Custom headers to include in webhook requests

webhooks[].timeoutMs

number

default:

8000

Request timeout in milliseconds (1000-30000)

webhooks[].retry

object

default:

{ mode: "default" }

Retry policy. 'default' retries on failure, 'none' disables retries

Webhook subscription example

```
// Webhook request example
curl -X POST "https://api.rtrvr.ai/agent" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Scrape the homepage and summarize it",
    "urls": ["https://example.com"],
    "webhooks": [
      {
        "url": "https://your-server.com/webhook",
        "events": ["rtrvr.execution.succeeded", "rtrvr.execution.failed"],
        "secret": "your-signing-secret",
        "headers": {
          "X-Custom-Header": "my-value"
        }
      }
    ]
  }'
```

#### Webhook Payload

When an event triggers, rtrvr sends a POST request with this envelope:

Webhook payload envelope

```
{
  "id": "whd_abc123",           // Unique delivery ID
  "event": "rtrvr.execution.succeeded",
  "createdAt": "2025-01-15T10:30:00.000Z",
  "data": {
    "trajectoryId": "exec_xyz789",
    "status": "success",
    "taskRef": "gs://bucket/user-tasks/uid/exec_xyz789/workflow.json",
    "responseRef": { ... },    // Full response snapshot when > 1MB
    "output": { ... },         // Inline preview payload
    "outputRef": { ... },      // Optional large output download reference
    "resultRef": { ... },      // Optional large result download reference
    "usage": {
      "creditsUsed": 0.15,
      "creditsLeft": 99.85
    }
  }
}
```

#### Signature Verification

If you provide a `secret`, verify the signature:

Verify X-Rtrvr-Signature

```
// Node.js signature verification
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const [tPart, v1Part] = signature.split(',');
  const timestamp = tPart.split('=')[1];
  const receivedSig = v1Part.split('=')[1];

  const signedPayload = timestamp + '.' + JSON.stringify(payload);
  const expectedSig = crypto
    .createHmac('sha256', secret)
    .update(signedPayload)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(receivedSig),
    Buffer.from(expectedSig)
  );
}
```

Response metadata:

The API response includes

metadata.webhooks:

{

requested: number, attempted: number

}

showing how many webhooks were configured and enqueued.

Store & reuse webhooks

Save your webhook endpoints in [Cloud → Webhooks](https://www.rtrvr.ai/cloud?view=webhooks) to quickly attach them to any execution without re-entering the URL, secret, and events each time.

Every call returns an `AgentApiResponse`:

AgentApiResponse (conceptual)

```
interface AgentApiResponse {
  success: boolean;
  status: 'success' | 'error' | 'cancelled' | 'requires_input' | 'executing';

  trajectoryId: string;
  phase: number;

  // Rich output blocks
  output: ApiOutputBlock[];
  // Note: in debug mode, tool_result blocks may include outputRef/resultRef
  // when large per-step payloads are stored out-of-line.

  // Convenience view of final output
  result?: {
    text?: string;
    json?: any;
  };

  // Present when verbosity !== 'final'
  steps?: ApiStepSummary[];

  usage: {
    creditsUsed: number;
    creditsLeft?: number;
    currentCreditsUsed?: number;
    expiryReason?: string;
  };

  metadata: {
    taskRef: string;
    inlineOutputMaxBytes: number;
    toolsUsed: string[];
    outputTooLarge?: boolean;
    responseRef?: StorageReference;
  };

  warnings?: string[];
  error?: string;

  // Continuation payload for advanced clients
  history?: {
    previousSteps?: PlannerPreviousStep[];
    lastToolPreviousSteps?: ToolPreviousSteps;
  };
}
```

### Output blocks & result

The low-level `output` is an array of blocks:

output[].type

"text" | "json" | "tool_result"

Block type: final text, JSON payload, or detailed tool result (debug mode).

output[].text

string

Present when type = 'text'.

output[].data

any

Present when type = 'json'.

output[].tool_result

…

When type = 'tool_result', includes stepId, toolName, args, inline output preview, optional outputRef/resultRef, thought, etc. Only present when verbosity = 'debug'.

`result.text` is the concatenation of all text blocks. `result.json` is either the single JSON block, or an array of JSON blocks if the workflow produced multiple.

### Steps & usage

When `response.verbosity` is `"steps"` or `"debug"`, you also get `steps: ApiStepSummary[]`:

steps[].toolName

string

Which tool ran in this step (e.g. 'sheets_workflow', 'act_on_tab').

steps[].status

ExecutionStatus

success, error, executing, etc. per step.

steps[].duration

number

Execution time in ms for this step (when available).

steps[].creditsUsed

number

Credits consumed by this step, useful for analytics.

steps[].hasOutput

boolean

Whether this step produced output or an outputRef.

steps[].hasSheets

boolean

Whether this step produced or touched tabular data.

steps[].hasGeneratedContent

boolean

Whether this step generated external content (docs, slides, etc.).

`usage` mirrors your credit accumulator and is ideal for per-customer dashboards and server-side cost control.

### Large output handling

When the full response exceeds `inlineOutputMaxBytes`:

- • The full response is snapshot to storage under `metadata.responseRef`.
- • The inline `output`/`result` fields remain as preview content for UX.
- • Debug `tool_result` blocks may include `outputRef` / `resultRef` for full per-step payloads.
- • `metadata.outputTooLarge` is set to `true`.

Client pattern: render the preview for UX, but fetch `responseRef.downloadUrl` from your backend when you need the full payload.

### status & success

status

"success" | "error" | "cancelled" | "requires_input" | "executing"

Execution-level status. success implies success = true; all others imply success = false.

- • `"success"` – Final result is available in `result` and `output`.
- • `"error"` – Workflow failed. You still get `usage`, `steps` (if enabled), and partial output if any.
- • `"cancelled"` – Client abort or timeout. Credits are accounted for partial work.
- • `"requires_input"` – Planner paused because it needs human answers (ASK_USER).

Continuation pattern:

1. When you see `status: "requires_input"`, surface your own UI to collect missing info.
2. On the next call, send the same `trajectoryId` with `history.continue = true` and the updated `history` object returned from the previous response.

rtrvr supports **view-only live VNC streaming** for any execution. Watch the browser in real-time, embed it in your app via iframe, or build custom viewers using the VNC websocket URL.

Use Cases

- • **Debugging:** Watch exactly what the browser is doing during automation
- • **Demos:** Show clients real-time browser activity
- • **Dashboards:** Embed live views in internal tools
- • **Quality assurance:** Monitor batch jobs visually

### Key Concepts

trajectoryId = executionId

In VNC endpoints, `executionId` refers to your `trajectoryId`. They are the same identifier.

vncScope

`"root"` = main browser only (default).
`"all"` = main + all batch worker browsers.

shareKey

A secret token for public/share endpoints. Anyone with it can view (not control) the session until it expires.

Sessions

`root` = main browser session.
`batch` = worker sessions (when vncScope="all").

### Step 1: Enable VNC on Execution

Add `options.ui.enableVnc: true` to your execute request.** Pro tip:** Generate your own `trajectoryId` upfront so you can request the embed URL immediately without waiting for the response.

Enable VNC on execution

```
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "trajectoryId": "0f3f2d33-0f6a-4d79-bb3d-56c2d4d7c2a1",
    "input": "Go to example.com and summarize the homepage",
    "urls": ["https://example.com"],
    "options": {
      "ui": {
        "enableVnc": true,
        "vncScope": "root"
      }
    }
  }'
```

### Step 2: Get the Embed URL

Call `POST /vnc/share` with the `executionId` (same as your trajectoryId). This returns an `embedUrl` ready for iframe embedding.

POST

https://api.rtrvr.ai

/vnc/share

executionId

string

required

The trajectoryId from your execute request

rotate

boolean

default:

false

Set true to generate a new share key (invalidates previous share URLs)

Get embed URL

```
curl -X POST https://api.rtrvr.ai/vnc/share \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "executionId": "0f3f2d33-0f6a-4d79-bb3d-56c2d4d7c2a1",
    "rotate": false
  }'
```

#### Response

Share response

```
{
  "ok": true,
  "executionId": "0f3f2d33-0f6a-4d79-bb3d-56c2d4d7c2a1",
  "embedUrl": "https://api.rtrvr.ai/agent/vnc/embed/0f3f2d33-0f6a-4d79-bb3d-56c2d4d7c2a1#key=<SHARE_KEY>",
  "shareKeyExpiresAt": 1730000000
}
```

### Step 3: Embed in Your App

Use the `embedUrl` directly in an iframe. The hosted page handles everything: loading the VNC viewer, connecting to the relay, and auto-refreshing tokens.

Embed in iframe

```
<iframe
  src="https://api.rtrvr.ai/agent/vnc/embed/0f3f2d33-0f6a-4d79-bb3d-56c2d4d7c2a1#key=YOUR_SHARE_KEY"
  style="width: 100%; height: 720px; border: 0; border-radius: 12px;"
  allow="clipboard-read; clipboard-write"
></iframe>
```

Why the share key is in the fragment (#key=...)

The share key is placed in the URL fragment so it's **never sent to servers** in HTTP requests by default. The embed page reads it client-side and sends it in an Authorization header when calling VNC endpoints.

### Complete Integration Example

Full VNC integration (JavaScript)

```
const API_URL = "https://api.rtrvr.ai";
const API_KEY = "YOUR_API_KEY";

async function startExecutionWithVnc(input, urls) {
  // 1. Generate your own trajectoryId for immediate embed
  const trajectoryId = crypto.randomUUID();
  
  // 2. Start execution with VNC enabled
  const executePromise = fetch(`${API_URL}/agent`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      trajectoryId,
      input,
      urls,
      options: {
        ui: {
          enableVnc: true,
          vncScope: "root"  // or "all" for batch workers
        }
      }
    }),
  });
  
  // 3. Immediately request embed URL (don't wait for execute)
  const shareRes = await fetch(`${API_URL}/vnc/share`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ 
      executionId: trajectoryId,
      rotate: false 
    }),
  });
  
  const shareData = await shareRes.json();
  
  if (shareData.ok) {
    // 4. Embed the VNC view
    const iframe = document.createElement("iframe");
    iframe.src = shareData.embedUrl;
    iframe.style.cssText = "width:100%;height:720px;border:0;border-radius:12px;";
    iframe.allow = "clipboard-read; clipboard-write";
    document.getElementById("vnc-container").appendChild(iframe);
  }
  
  // 5. Wait for execution to complete
  const executeRes = await executePromise;
  const result = await executeRes.json();
  
  return { result, embedUrl: shareData.embedUrl };
}

// Usage
startExecutionWithVnc(
  "Scrape the top 5 articles from Hacker News",
  ["https://news.ycombinator.com"]
).then(({ result, embedUrl }) => {
  console.log("Execution complete:", result);
  console.log("VNC embed URL:", embedUrl);
});
```

Full VNC integration (Python)

```
import uuid
import requests
import threading

API_URL = "https://api.rtrvr.ai"
API_KEY = "YOUR_API_KEY"

def start_execution_with_vnc(input_text: str, urls: list[str]):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 1. Generate your own trajectoryId
    trajectory_id = str(uuid.uuid4())
    
    # 2. Start execution in background thread
    def execute():
        return requests.post(
            f"{API_URL}/agent",
            headers=headers,
            json={
                "trajectoryId": trajectory_id,
                "input": input_text,
                "urls": urls,
                "options": {
                    "ui": {
                        "enableVnc": True,
                        "vncScope": "root"  # or "all" for batch workers
                    }
                }
            },
            timeout=300
        ).json()
    
    execute_thread = threading.Thread(target=execute)
    execute_thread.start()
    
    # 3. Immediately get embed URL
    share_res = requests.post(
        f"{API_URL}/vnc/share",
        headers=headers,
        json={
            "executionId": trajectory_id,
            "rotate": False
        }
    ).json()
    
    if share_res.get("ok"):
        print(f"VNC Embed URL: {share_res['embedUrl']}")
        print(f"Share key expires: {share_res['shareKeyExpiresAt']}")
    
    # 4. Wait for execution
    execute_thread.join()
    
    return {
        "trajectory_id": trajectory_id,
        "embed_url": share_res.get("embedUrl")
    }

# Usage
result = start_execution_with_vnc(
    "Go to example.com and take a screenshot",
    ["https://example.com"]
)
print(f"Embed in iframe: {result['embed_url']}")
```

Full VNC flow (cURL)

```
# 1. Start execution with VNC enabled (use your own trajectoryId)
TRAJECTORY_ID="$(uuidgen)"

curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"trajectoryId\": \"$TRAJECTORY_ID\",
    \"input\": \"Go to example.com and summarize\",
    \"urls\": [\"https://example.com\"],
    \"options\": {
      \"ui\": {
        \"enableVnc\": true,
        \"vncScope\": \"root\"
      }
    }
  }" &

# 2. Immediately get the embed URL (don't wait for execute)
curl -X POST https://api.rtrvr.ai/vnc/share \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"executionId\": \"$TRAJECTORY_ID\",
    \"rotate\": false
  }"

# Response contains embedUrl - use it in an iframe
```

### Advanced: Build a Custom Viewer

For custom UIs, use the public VNC endpoints to list sessions and get websocket URLs. These endpoints require the `shareKey` (from the embed URL) as a Bearer token.

#### List Sessions

GET

/vnc-public/sessions?executionId={executionId}

List VNC sessions (public endpoint)

```
curl "https://api.rtrvr.ai/vnc-public/sessions?executionId=0f3f2d33-0f6a-4d79-bb3d-56c2d4d7c2a1" \
  -H "Authorization: Bearer YOUR_SHARE_KEY"

# Response:
# {
#   "ok": true,
#   "executionId": "0f3f2d33-0f6a-4d79-bb3d-56c2d4d7c2a1",
#   "sessions": [
#     {
#       "sessionId": "0f3f2d33-0f6a-4d79-bb3d-56c2d4d7c2a1",
#       "kind": "root",
#       "batchIndex": null,
#       "state": "running",
#       "expiresAt": 1730001234
#     }
#   ]
# }
```

#### Get Viewer Token & WebSocket URL

GET

/vnc-public/token?executionId={id}&sessionId={id}

Get VNC token and websocket URL

```
curl "https://api.rtrvr.ai/vnc-public/token?executionId=0f3f2d33-0f6a-4d79-bb3d-56c2d4d7c2a1&sessionId=0f3f2d33-0f6a-4d79-bb3d-56c2d4d7c2a1" \
  -H "Authorization: Bearer YOUR_SHARE_KEY"

# Response:
# {
#   "ok": true,
#   "executionId": "0f3f2d33-0f6a-4d79-bb3d-56c2d4d7c2a1",
#   "sessionId": "0f3f2d33-0f6a-4d79-bb3d-56c2d4d7c2a1",
#   "wsUrl": "wss://relay.rtrvr.ai/vnc?token=<JWT>",
#   "expiresAt": 1730000600
# }
```

Token refresh:

VNC tokens expire (~10 minutes). For long-running sessions, refresh the token before expiry by calling

/vnc-public/token

again.

### Authenticated VNC Endpoints (Owner Access)

These endpoints use your API key directly (no share key needed). Useful when you don't want to expose share links.

GET /vnc/sessions

endpoint

List sessions for an execution. Add ?withToken=1 to include wsUrl for each session.

GET /vnc/token

endpoint

Get viewer token + wsUrl. Add ?createIfMissing=1 to auto-create the session doc.

POST /vnc/share

endpoint

Generate/rotate a share key and get embedUrl.

Authenticated session list with tokens

```
curl "https://api.rtrvr.ai/vnc/sessions?executionId=YOUR_TRAJECTORY_ID&withToken=1" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### VNC Endpoint Reference

Endpoint

Auth

Description

POST /vnc/share

API Key

Get embedUrl + shareKey

GET /vnc/sessions

API Key

List sessions (owner access)

GET /vnc/token

API Key

Get wsUrl token (owner access)

GET /vnc-public/sessions

Share Key

List sessions (public/share)

GET /vnc-public/token

Share Key

Get wsUrl token (public/share)

GET /vnc/embed/:executionId

Share Key (in #fragment)

Hosted noVNC viewer page

### Security Best Practices

- • **Treat shareKey like a password:** Anyone with it can view your browser session
- • **Use fragment URLs:** The `#key=...` format prevents the key from appearing in server logs
- • **Rotate when needed:** Call `POST /vnc/share` with `rotate: true` to invalidate old links
- • **Use vncScope wisely:** Only use `"all"` if you need to see batch worker browsers
- • **View-only:** Share links cannot control the browser, only view it

💡 Tip:

Using Google tools? First connect your Google account at

rtrvr.ai/cloud → Sheets

cURL

```
# ═══════════════════════════════════════════════════════════════
# BASIC EXAMPLES
# ═══════════════════════════════════════════════════════════════

# 1. Simple page summarization
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Summarize the main points of this page in 5 bullet points.",
    "urls": ["https://example.com/blog/ai-trends-2025"],
    "response": { "verbosity": "final" }
  }'

# 2. With JSON schema for structured output
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Extract article title, author, and publish date.",
    "urls": ["https://example.com/blog/article"],
    "schema": {
      "type": "object",
      "properties": {
        "title": { "type": "string" },
        "author": { "type": "string" },
        "publishDate": { "type": "string" }
      },
      "required": ["title"]
    }
  }'

# ═══════════════════════════════════════════════════════════════
# FILE INPUT EXAMPLES
# ═══════════════════════════════════════════════════════════════

# 3. Analyze a PDF document
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Extract key financial metrics from this quarterly report.",
    "files": [
      {
        "displayName": "Q3-Report.pdf",
        "uri": "https://firebasestorage.googleapis.com/v0/b/bucket/o/files%2Freport.pdf?alt=media&token=abc",
        "mimeType": "application/pdf"
      }
    ],
    "schema": {
      "type": "object",
      "properties": {
        "revenue": { "type": "string" },
        "profit": { "type": "string" },
        "growth_rate": { "type": "string" }
      }
    }
  }'

# 4. Analyze an image
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Describe this UI screenshot and identify usability issues.",
    "files": [
      {
        "displayName": "app-screenshot.png",
        "uri": "gs://my-bucket/screenshots/app.png",
        "mimeType": "image/png"
      }
    ]
  }'

# 5. Compare two documents
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Compare these contracts and list all differences.",
    "files": [
      {
        "displayName": "contract-v1.pdf",
        "uri": "https://firebasestorage.googleapis.com/.../v1.pdf?...",
        "mimeType": "application/pdf"
      },
      {
        "displayName": "contract-v2.pdf",
        "uri": "https://firebasestorage.googleapis.com/.../v2.pdf?...",
        "mimeType": "application/pdf"
      }
    ]
  }'

# ═══════════════════════════════════════════════════════════════
# DATA INPUT EXAMPLES
# ═══════════════════════════════════════════════════════════════

# 6. CSV enrichment (inline)
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "For each company, find their website and a one-sentence description.",
    "dataInputs": [
      {
        "description": "Companies to enrich",
        "format": "csv",
        "inline": "company\nOpenAI\nAnthropic\nGoogle DeepMind"
      }
    ],
    "response": { "verbosity": "steps" }
  }'

# 7. JSON array processing
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Classify each review as positive, negative, or neutral.",
    "dataInputs": [
      {
        "description": "Reviews",
        "format": "json",
        "inline": "[{\"text\":\"Great product!\"},{\"text\":\"Terrible support.\"},{\"text\":\"It works okay.\"}]"
      }
    ]
  }'

# 8. XLSX from URL
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Summarize the sales pipeline metrics.",
    "dataInputs": [
      {
        "description": "Sales pipeline",
        "format": "xlsx",
        "url": "https://example.com/data/pipeline.xlsx"
      }
    ]
  }'

# ═══════════════════════════════════════════════════════════════
# COMBINED: FILES + DATA + BROWSING
# ═══════════════════════════════════════════════════════════════

# 9. Complex workflow: Analyze resume + scrape job posting + match
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Analyze the resume, scrape the job posting, and score the candidate fit (1-10) with reasoning.",
    "urls": ["https://company.com/careers/senior-engineer"],
    "files": [
      {
        "displayName": "candidate-resume.pdf",
        "uri": "https://firebasestorage.googleapis.com/.../resume.pdf?...",
        "mimeType": "application/pdf"
      }
    ],
    "schema": {
      "type": "object",
      "properties": {
        "fitScore": { "type": "number" },
        "strengths": { "type": "array", "items": { "type": "string" } },
        "gaps": { "type": "array", "items": { "type": "string" } },
        "recommendation": { "type": "string" }
      }
    }
  }'

# ═══════════════════════════════════════════════════════════════
# GOOGLE SHEETS
# ═══════════════════════════════════════════════════════════════

# 10. Create new Google Sheet
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Scrape all products and save to Google Sheets.",
    "urls": ["https://example.com/products"],
    "tools": { "enableAdditionalTools": ["generate_sheets"] }
  }'

# 11. Append to existing Google Sheet
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Scrape new leads and add to my existing sheet.",
    "urls": ["https://linkedin.com/search/..."],
    "reuseArtifacts": {
      "mode": "force",
      "targets": {
        "sheets": {
          "sheetId": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
          "tabTitle": "Leads",
          "tabMode": "SAME_TAB"
        }
      }
    },
    "tools": { "enableAdditionalTools": ["generate_sheets"] }
  }'

# ═══════════════════════════════════════════════════════════════
# GOOGLE SLIDES
# ═══════════════════════════════════════════════════════════════

# 12. Create new presentation
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Create a 5-slide presentation summarizing key points. Include title, 3 content slides, and conclusion.",
    "urls": ["https://example.com/blog/industry-trends-2025"],
    "tools": { "enableAdditionalTools": ["generate_slides"] }
  }'

# 13. Append to existing presentation
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Add 3 slides with competitor analysis to the existing presentation.",
    "urls": ["https://competitor.com/products"],
    "reuseArtifacts": {
      "mode": "force",
      "targets": {
        "slides": {
          "presentationId": "1abc123_your_presentation_id",
          "mode": "APPEND"
        }
      }
    },
    "tools": { "enableAdditionalTools": ["generate_slides"] }
  }'

# ═══════════════════════════════════════════════════════════════
# GOOGLE DOCS
# ═══════════════════════════════════════════════════════════════

# 14. Create new Google Doc
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Create a detailed research report about this company including products, leadership, and news.",
    "urls": ["https://example.com/about", "https://example.com/news"],
    "tools": { "enableAdditionalTools": ["generate_docs"] }
  }'

# 15. Append to existing Google Doc
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Add a new section summarizing this weeks market news.",
    "urls": ["https://news.example.com/markets"],
    "reuseArtifacts": {
      "mode": "force",
      "targets": {
        "docs": {
          "docId": "1abc123_your_doc_id",
          "mode": "APPEND"
        }
      }
    },
    "tools": { "enableAdditionalTools": ["generate_docs"] }
  }'

# ═══════════════════════════════════════════════════════════════
# PDF GENERATION & FILLING
# ═══════════════════════════════════════════════════════════════

# 16. Generate new PDF
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Create a PDF invoice: 3x Widget Pro at $99 each, customer: Acme Corp.",
    "tools": { "enableAdditionalTools": ["generate_pdfs"] }
  }'

# 17. Fill PDF form template
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Fill the W-9 form with: Name: John Smith, Business: Smith Consulting LLC",
    "reuseArtifacts": {
      "mode": "force",
      "targets": {
        "pdfs": { "templateFileId": "1xyz_w9_template_id" }
      }
    },
    "tools": { "enableAdditionalTools": ["pdf_filling"] }
  }'

# ═══════════════════════════════════════════════════════════════
# WEB DASHBOARDS
# ═══════════════════════════════════════════════════════════════

# 18. Generate interactive dashboard
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Create an interactive dashboard showing sales by region with charts.",
    "dataInputs": [{
      "description": "Sales data",
      "format": "csv",
      "inline": "region,sales,month\nNorth,50000,Jan\nSouth,42000,Jan\nEast,38000,Jan"
    }],
    "tools": { "enableAdditionalTools": ["generate_websites"] }
  }'

# ═══════════════════════════════════════════════════════════════
# INTERACTIVE WORKFLOWS (ask_questions)
# ═══════════════════════════════════════════════════════════════

# 19. Enable follow-up questions
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Help me find the best flight from NYC to London.",
    "urls": ["https://flights.example.com"],
    "tools": { "enableAdditionalTools": ["ask_questions"] }
  }'

# 20. Continue after requires_input status
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Direct flights only, economy class, morning departure.",
    "trajectoryId": "traj_from_previous_response",
    "history": { "continue": true }
  }'

# ═══════════════════════════════════════════════════════════════
# MULTI-PHASE WORKFLOWS
# ═══════════════════════════════════════════════════════════════

# 21. Phase 1: Discovery
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Find the top 10 AI startups in healthcare.",
    "urls": ["https://techcrunch.com/tag/ai-healthcare"],
    "phase": 1
  }'

# 22. Phase 2: Enrichment (same trajectoryId)
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Get funding details and executives for each startup.",
    "trajectoryId": "traj_from_phase1",
    "phase": 2,
    "tools": { "enableAdditionalTools": ["generate_sheets"] }
  }'

# 23. Phase 3: Report
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Create a presentation with investment recommendations.",
    "trajectoryId": "traj_from_phase1",
    "phase": 3,
    "tools": { "enableAdditionalTools": ["generate_slides"] }
  }'

# ═══════════════════════════════════════════════════════════════
# CUSTOM TOOLS
# ═══════════════════════════════════════════════════════════════

# 24. Use custom/user-defined tools
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Find leads and add them to our CRM.",
    "urls": ["https://linkedin.com/search/..."],
    "tools": {
      "mode": "allowlist",
      "userDefined": ["add_to_crm", "enrich_lead"]
    }
  }'
  # ═══════════════════════════════════════════════════════════════
# VNC LIVE VIEW EXAMPLES
# ═══════════════════════════════════════════════════════════════

# 25. Start execution with VNC enabled
TRAJECTORY_ID="$(uuidgen)"
curl -X POST https://api.rtrvr.ai/agent \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"trajectoryId\": \"$TRAJECTORY_ID\",
    \"input\": \"Navigate to example.com and fill out the contact form\",
    \"urls\": [\"https://example.com/contact\"],
    \"options\": {
      \"ui\": {
        \"enableVnc\": true,
        \"vncScope\": \"root\"
      }
    }
  }"

# 26. Get embeddable VNC URL
curl -X POST https://api.rtrvr.ai/vnc/share \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"executionId\": \"$TRAJECTORY_ID\",
    \"rotate\": false
  }"

# 27. List VNC sessions (authenticated)
curl "https://api.rtrvr.ai/vnc/sessions?executionId=$TRAJECTORY_ID&withToken=1" \
  -H "Authorization: Bearer YOUR_API_KEY"

# 28. Get VNC token (authenticated)
curl "https://api.rtrvr.ai/vnc/token?executionId=$TRAJECTORY_ID&sessionId=$TRAJECTORY_ID" \
  -H "Authorization: Bearer YOUR_API_KEY"

# 29. List sessions with share key (public)
curl "https://api.rtrvr.ai/vnc-public/sessions?executionId=$TRAJECTORY_ID" \
  -H "Authorization: Bearer YOUR_SHARE_KEY"

# 30. Get VNC token with share key (public)
curl "https://api.rtrvr.ai/vnc-public/token?executionId=$TRAJECTORY_ID&sessionId=$TRAJECTORY_ID" \
  -H "Authorization: Bearer YOUR_SHARE_KEY"
```

### Ready to automate?

Join teams using rtrvr.ai to build playful, powerful web automation workflows.
