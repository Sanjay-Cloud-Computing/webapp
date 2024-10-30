import os
import requests
from dotenv import load_dotenv

def send_email_via_sendgrid(to_email, subject, content):
    """
    Sends an email using the SendGrid API.
    
    Parameters:
        to_email (str): The recipient's email address.
        subject (str): The subject of the email.
        content (str): The plain text content of the email.

    Returns:
        response: The response object from the SendGrid API request.
    """
    # Ensure the SendGrid API key is available as an environment variable
    
    load_dotenv()
    sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
    if not sendgrid_api_key:
        raise ValueError("SendGrid API key is missing. Set the SENDGRID_API_KEY environment variable.")

    # Define the SendGrid API endpoint and headers
    url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {sendgrid_api_key}",
        "Content-Type": "application/json"
    }

    # Define the payload for the email
    data = {
        "personalizations": [{
            "to": [{"email": to_email}]
        }],
        "from": {"email": "noreply@dev.cloudsan.me"},
        "subject": subject,
        "content": [{
            "type": "text/plain",
            "value": content
        }]
    }

    # Make the POST request to the SendGrid API
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.status_code, response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to send email: {e}")
        return None, str(e)
