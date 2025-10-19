import os
import requests
from dotenv import load_dotenv

load_dotenv()


API_ENDPOINT = os.getenv("API_ENDPOINT")
API_KEY = os.getenv("API_KEY")
from_email = os.getenv("FROM_EMAIL")
to_email = os.getenv("TO_EMAIL")

def send_email(to, subject, body):

    data = {
        'from': from_email,
        'to': to,
        'subject': subject,
        'text': body
    }

    response = requests.post(
        API_ENDPOINT,
        auth=('api', API_KEY),
        data=data
    )

    if response.status_code == 200:
        print('Email sent successfully!')
    else:
        print('An error occurred while sending the email.')
# Example usage

subject = 'Email Subject'
body = 'Email body content'
send_email(to_email, subject, body)