import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
from gensim import corpora, models, similarities

from gensim.summarization import summarize
from flask import Flask, render_template

app = Flask(__name__)

# Email configurations
EMAIL = "aakshita_be22@thapar.edu"
PASSWORD = "VIN13750#lms"
IMAP_SERVER = "imap.thapar.edu"
DOMAIN = "thapar.edu"  # Change to @thapar.edu domain

def fetch_emails():
    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')

    # Search for emails from the specified domain
    result, data = mail.search(None, f'(FROM "@{DOMAIN}")')
    email_ids = data[0].split()

    emails = []
    for email_id in email_ids:
        result, data = mail.fetch(email_id, "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)
        subject = decode_header(msg["Subject"])[0][0]
        if isinstance(subject, bytes):
            subject = subject.decode()
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                if "attachment" not in content_disposition:
                    charset = str(part.get_content_charset())
                    if charset:
                        body = part.get_payload(decode=True).decode(charset, "ignore")
                    else:
                        body = part.get_payload(decode=True).decode("utf-8", "ignore")
        else:
            content_type = msg.get_content_type()
            body = msg.get_payload(decode=True).decode("utf-8", "ignore")
        emails.append((subject, body))
    mail.logout()
    return emails

def summarize_emails(emails):
    summaries = []
    for subject, body in emails:
        # Extract text from HTML
        soup = BeautifulSoup(body, "html.parser")
        text = soup.get_text()
        # Summarize the email content
        summary = summarize(text)
        summaries.append((subject, summary))
    return summaries

@app.route('/')
def index():
    emails = fetch_emails()
    summaries = summarize_emails(emails)
    return render_template('index.html', summaries=summaries)

if __name__ == '__main__':
    app.run(debug=True)
