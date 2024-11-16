from app.utilities.email_utils import send_email_via_sendgrid

def send_email(user_email,subject,content):
    status, response = send_email_via_sendgrid(to_email=user_email, subject=subject, content=content)
    
    if status == 202:
        print("Email sent successfully.")
    else:
        print("Failed to send email:", response)
