import os
import re
import email
from imapclient import IMAPClient

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_APP_PASSWORD"]

def extract_json(body):
    match = re.search(r"JSON_START\s*([\s\S]*?)\s*JSON_END", body)
    if not match:
        print("❌ No JSON block found")
        return None
    return match.group(1).strip()

def save_files(json_data):
    import json

    try:
        json.loads(json_data)  # validate JSON
    except Exception as e:
        print("❌ Invalid JSON:", e)
        return False

    with open("tvJSON.json", "w") as f:
        f.write(json_data)

    with open("docs/tvJSON.json", "w") as f:
        f.write(json_data)

    print("✅ JSON files updated")
    return True

def get_email_body(msg):
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()

            if content_type == "text/plain":
                try:
                    return part.get_payload(decode=True).decode(errors="ignore")
                except:
                    continue

            elif content_type == "text/html" and not body:
                try:
                    body = part.get_payload(decode=True).decode(errors="ignore")
                except:
                    continue
    else:
        try:
            body = msg.get_payload(decode=True).decode(errors="ignore")
        except:
            body = ""

    return body

def main():
    print("🚀 Script started")

    with IMAPClient("imap.gmail.com") as server:
        print("🔐 Logging in...")
        server.login(GMAIL_USER, GMAIL_PASS)

        server.select_folder("INBOX")
        print("📥 Checking inbox...")

        messages = server.search(["UNSEEN"])
        print(f"📨 Found {len(messages)} unread emails")

        if not messages:
            return

        for msgid, data in server.fetch(messages, ["RFC822"]).items():
            msg = email.message_from_bytes(data[b"RFC822"])

            subject = msg["subject"] or ""
            print(f"✉️ Subject: {subject}")

            body = get_email_body(msg)

            # Trigger condition (subject OR body)
            if "tvjson update" in subject.lower() or "tvjson update" in body.lower():
                print("✅ Trigger matched")

                json_data = extract_json(body)

                if json_data:
                    if save_files(json_data):
                        server.add_flags(msgid, ["\\Seen"])
                        print("📌 Email marked as read")
                else:
                    print("⚠️ JSON not found in email")
            else:
                print("⏭️ Skipped (no trigger match)")

if __name__ == "__main__":
    main()
