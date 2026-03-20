import os
import re
import email
from imapclient import IMAPClient

GMAIL_USER = os.environ["GMAIL_USER"]
GMAIL_PASS = os.environ["GMAIL_APP_PASSWORD"]

def extract_json(body):
    match = re.search(r"JSON_START\s*([\s\S]*?)\s*JSON_END", body)
    if not match:
        return None
    return match.group(1).strip()

def save_files(json_data):
    import json

    # validate JSON
    json.loads(json_data)

    with open("tvJSON.json", "w") as f:
        f.write(json_data)

    with open("docs/tvJSON.json", "w") as f:
        f.write(json_data)

def main():
    with IMAPClient("imap.gmail.com") as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.select_folder("INBOX")

        messages = server.search(["UNSEEN"])

        for msgid, data in server.fetch(messages, ["RFC822"]).items():
            msg = email.message_from_bytes(data[b"RFC822"])

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()

            if "tvjson update" in body.lower():
                json_data = extract_json(body)

                if json_data:
                    save_files(json_data)
                    server.add_flags(msgid, ["\\Seen"])

if __name__ == "__main__":
    main()
