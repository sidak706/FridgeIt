# import google.generativeai as genai

# genai.configure(api_key="AIzaSyB_44dv2A-soBHojY4AzayMR5lTvdIeKqY")
# model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content("Give an estimate for how many days/months it takes for chicken to expire in the freezer? GIVE ONLY THE NUMBER")

# name = "something"
# genai.configure(api_key="AIzaSyB_44dv2A-soBHojY4AzayMR5lTvdIeKqY")
# model = genai.GenerativeModel("gemini-1.5-flash")
# response = model.generate_content(f"""Give an estimate for how many days/months it
#                                    takes for {name} to expire in the fridge? GIVE the answer in a format
#                                    where the first part of your response is 1 if your suggestion is months
#                                    0 otherwise. The second part of your response should be the actual days/months
#                                    value. For example, if your answer is 3 months, your response should be
#                                    1 3 , if its 2 days, it should be 1 2. Do not include hyphenated numbers in your
#                                    response, if your answer is 2-3 days, just say 0 2, i.e only give the lower bound. 
#                                    If you think the dish name is invalid, your response should be -1.""")

# response2 = response.text
# print(response2[2])

# print(response.text)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(userEmail, food, time_left, fridge, expired):
    # Configuration for SendGrid
    smtp_server = "smtp.sendgrid.net"
    port = 587  # TLS port (you could also use port 465 for SSL)
    username = "apikey"  # The username is always 'apikey' for SendGrid
    # password = "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"  # Your API Key
    password = "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"  # Your API Key
    sender_email = "fridgeit720@gmail.com"
    receiver_email = userEmail
    # Create the email
    subject = ""
    body = """
    Dish approaching Expiry
    """


    
    # Create MIMEText object for the body and a MIMEMultipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject


    # Attach the body to the message
    message.attach(MIMEText(body, "plain"))

    # Sending email through SendGrid SMTP
    try:
        # Connect to the server
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()  # Secure the connection using TLS
            server.login(username, password)  # Log in with the SendGrid API key
            server.sendmail(sender_email, receiver_email, message.as_string())  # Send the email
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


send_email("sidaksarora@gmail.com", 1, 1, 1, 1)