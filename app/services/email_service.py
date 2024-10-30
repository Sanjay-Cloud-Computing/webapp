# import os
# import sendgrid
# from sendgrid.helpers.mail import Mail, Email, To, Content
# from dotenv import load_dotenv

# load_dotenv()

# SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
# sg_client = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)

# def send_email(to_email, subject, content_text):
#     from_email = Email("noreply@dev.cloudsan.me")
#     to_email = To(to_email)
#     content = Content("text/plain", content_text)
#     mail = Mail(from_email, to_email, subject, content)

#     try:
#         response = sg_client.send(mail)
#         print(f"Email sent to {to_email}: Status Code {response.status_code}")
#         return response
#     except Exception as e:
#         print(f"Error sending email: {e}")
#         raise

from app.utilities.email_utils import send_email_via_sendgrid

def send_email(user_email,subject,content):
    status, response = send_email_via_sendgrid(to_email=user_email, subject=subject, content=content)
    
    if status == 202:
        print("Email sent successfully.")
    else:
        print("Failed to send email:", response)
