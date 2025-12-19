import requests
import csv
import os
import time
from datetime import datetime, timezone

# --- Configuration ---
ACCESS_TOKEN = os.getenv('INTERCOM_ACCESS_TOKEN')
if not ACCESS_TOKEN:
    raise ValueError("INTERCOM_ACCESS_TOKEN environment variable not set.")

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Intercom-Version": "2.10"
}

BASE_URL = "https://api.intercom.io"
CSV_FILENAME = "intercom_conversations_FULL.csv"

# --- Main Script Logic ---

def get_all_conversation_ids():
    print("Fetching all conversation IDs using the search endpoint...")
    conversation_ids = []
    payload = { "query": { "field": "created_at", "operator": ">", "value": 1 } }
    page_count = 1
    while True:
        try:
            response = requests.post(f"{BASE_URL}/conversations/search", headers=HEADERS, json=payload)
            response.raise_for_status()
            data = response.json()
            current_page_convos = data.get('conversations', [])
            if not current_page_convos: break
            for convo in current_page_convos:
                conversation_ids.append(convo['id'])
            print(f"Page {page_count}: Fetched {len(current_page_convos)} conversations. Total so far: {len(conversation_ids)}")
            pagination_data = data.get('pages', {})
            if pagination_data.get('next'):
                payload['pagination'] = {"starting_after": pagination_data['next']['starting_after']}
                page_count += 1
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f"An API error occurred: {e}")
            break
    print(f"Total conversations found: {len(conversation_ids)}")
    return conversation_ids

def get_conversation_details(convo_id):
    initial_url = f"{BASE_URL}/conversations/{convo_id}?display_as=plaintext&include_translations=true"
    try:
        response = requests.get(initial_url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch details for conversation {convo_id}: {e}")
        return None

def format_transcript(conversation_obj):
    transcript_parts = []
    # Step 1: Get the initial message from the 'source' object
    source = conversation_obj.get('source', {})
    source_body = source.get('body', '')
    if source_body:
        created_at_unix = conversation_obj.get('created_at')
        created_at_iso = datetime.fromtimestamp(created_at_unix, timezone.utc).isoformat() if created_at_unix else "No Timestamp"
        author = source.get('author', {})
        author_name = author.get('name', f"Unknown {author.get('type')}")
        initial_message = (
            f"[{created_at_iso}] {author_name} ({author.get('type')} - initial message):\n"
            f"{source_body.strip()}"
        )
        transcript_parts.append(initial_message)
    # Step 2: Get all subsequent replies from 'conversation_parts'
    parts = conversation_obj.get('conversation_parts', {}).get('conversation_parts', [])
    for part in parts:
        body = part.get('body', '')
        if not body: continue
        created_at_unix = part.get('created_at')
        created_at_iso = datetime.fromtimestamp(created_at_unix, timezone.utc).isoformat() if created_at_unix else "No Timestamp"
        author = part.get('author', {})
        author_name = author.get('name', f"Unknown {author.get('type')}")
        part_type = part.get('part_type', 'message')
        formatted_part = (
            f"[{created_at_iso}] {author_name} ({author.get('type')} - {part_type}):\n"
            f"{body.strip()}"
        )
        transcript_parts.append(formatted_part)
    return "\n\n".join(transcript_parts)

def write_to_csv(conversations_data):
    if not conversations_data:
        print("No data to write to CSV.")
        return
    print(f"Writing data to {CSV_FILENAME}...")
    fieldnames = [
        'id', 'created_at', 'updated_at', 'state',
        'contact_type', 'contact_id', 'contact_name', 'contact_email',
        'first_message_body', 'full_conversation_transcript'
    ]
    with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for convo in conversations_data:
            source = convo.get('source', {})
            transcript = format_transcript(convo)
            contact = {}
            contacts_list = convo.get('contacts', {}).get('contacts', [])
            if contacts_list: contact = contacts_list[0]
            writer.writerow({
                'id': convo.get('id'),
                'created_at': convo.get('created_at'),
                'updated_at': convo.get('updated_at'),
                'state': convo.get('state'),
                'contact_type': contact.get('type'),
                'contact_id': contact.get('id'),
                'contact_name': contact.get('name'),
                'contact_email': contact.get('email'),
                'first_message_body': source.get('body', '').strip(),
                'full_conversation_transcript': transcript
            })
    print("Successfully wrote data to CSV.")

if __name__ == "__main__":
    ids = get_all_conversation_ids()
    all_details = []
    if ids:
        total_ids = len(ids)
        print(f"\nStarting to fetch details for {total_ids} conversations. This will take a while...")
        for i, convo_id in enumerate(ids, 1):
            if i % 50 == 0 or i == 1 or i == total_ids:
                print(f"Fetching details for conversation {i}/{total_ids} (ID: {convo_id})...")
            details = get_conversation_details(convo_id)
            if details:
                all_details.append(details)
            time.sleep(0.5)
    write_to_csv(all_details)