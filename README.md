# Intercom Conversation Exporter

A Python script that exports all Intercom conversations — including full message transcripts — to a CSV file using the Intercom REST API.

This was created out of neccessity for an Intercom region hosting migration and was helpful to me, maybe it will be helpful to someone else out there too!

---

## Features

- Fetches every conversation from your Intercom workspace using cursor-based pagination
- Retrieves full conversation details including all replies and message parts
- Formats complete transcripts with timestamps, author names, and message types
- Exports everything to a structured CSV file

---

## Requirements

- Python 3.7+
- [`requests`](https://pypi.org/project/requests/) library

Install dependencies:

```bash
pip install requests
```

---

## Setup

### 1. Get your Intercom Access Token

1. Go to your [Intercom Developer Hub](https://developers.intercom.com/)
2. Create or open an app, then navigate to **Authentication**
3. Copy your **Access Token**

### 2. Set the environment variable

**macOS / Linux:**
```bash
export INTERCOM_ACCESS_TOKEN="your_token_here"
```

**Windows (Command Prompt):**
```cmd
set INTERCOM_ACCESS_TOKEN=your_token_here
```

**Windows (PowerShell):**
```powershell
$env:INTERCOM_ACCESS_TOKEN="your_token_here"
```

---

## Usage

```bash
python intercom_export.py
```

The script will:
1. Search for all conversations in your workspace
2. Fetch full details for each one individually
3. Write everything to `intercom_conversations_FULL.csv` in the current directory

> **Note:** Large workspaces with thousands of conversations will take considerable time to export due to rate-limiting delays (0.5s per conversation). A workspace with 2,000 conversations will take roughly 15–20 minutes.

---

## Output

The output file `intercom_conversations_FULL.csv` contains the following columns:

| Column | Description |
|---|---|
| `id` | Intercom conversation ID |
| `created_at` | Unix timestamp of when the conversation was created |
| `updated_at` | Unix timestamp of when the conversation was last updated |
| `state` | Conversation state (e.g. `open`, `closed`, `snoozed`) |
| `contact_type` | Type of the primary contact (e.g. `user`, `lead`) |
| `contact_id` | Intercom ID of the primary contact |
| `contact_name` | Display name of the primary contact |
| `contact_email` | Email address of the primary contact |
| `first_message_body` | Plain text of the opening message |
| `full_conversation_transcript` | Full conversation thread with timestamps and authors |

### Transcript format

Each message in the `full_conversation_transcript` column is formatted as:

```
[2024-06-01T10:23:00+00:00] Jane Smith (user - initial message):
Hi, I'm having trouble with my account...

[2024-06-01T10:45:12+00:00] Support Agent (admin - comment):
Hi Jane! Happy to help...
```

---

## Configuration

The following constants at the top of the script can be adjusted:

| Constant | Default | Description |
|---|---|---|
| `CSV_FILENAME` | `intercom_conversations_FULL.csv` | Name of the output file |
| `Intercom-Version` (header) | `2.10` | Intercom API version to use |
| `time.sleep(0.5)` | `0.5` seconds | Delay between detail requests — increase if you hit rate limits |

---

## Troubleshooting

**`ValueError: INTERCOM_ACCESS_TOKEN environment variable not set`**
The script requires the token to be set as an environment variable before running. See the [Setup](#setup) section above.

**API errors / HTTP 429 (Too Many Requests)**
Increase the `time.sleep()` delay in the main loop to reduce the request rate.

**Empty CSV / no conversations fetched**
Check that your access token has the `Read conversations` permission scope in the Intercom Developer Hub.

**Missing contact name or email in output**
Some conversations may be initiated by anonymous leads without a name or email address on record. These fields will be blank for those rows.

---

## Notes

- Conversations are fetched in plain text format (`display_as=plaintext`) to avoid HTML in transcript output
- The initial search query uses `created_at > 1` as a way to match all conversations regardless of age
- Only the first associated contact is included per conversation; multi-contact conversations will only reflect the primary contact
