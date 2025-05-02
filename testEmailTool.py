import smtplib
from email.message import EmailMessage


msg = EmailMessage()
msg.set_content("This is a test email using the tool")

sendEmail = "j89666944@gmail.com"
msg['Subject'] = "Guitar Comparisons"
msg['From'] = sendEmail
msg['To'] = sendEmail


try:
	with smtplib.SMTP('smtp.gmail.com', 587) as server:
		server.ehlo()          # Identify with the server
		server.starttls()      # Secure the connection
		server.ehlo()          # Re-identify after starting TLS
		server.login(sendEmail, password)
		server.send_message(msg)
	print("Successfull")
except Exception as e:
	print(f"An error occurred: {e}")
