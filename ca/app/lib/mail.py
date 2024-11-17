import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

class Mail:
    def __init__(self, email_address: str = None, email_passwd: str = None):
        self.__EMAIL_ADDRESS = email_address or os.environ['EMAIL_ADDRESS']
        self.__EMAIL_PASSWD = email_passwd or os.environ['EMAIL_PASSWD']

    def send_mail(self, subject: str, to: str, file_paths: list[str]):
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.__EMAIL_ADDRESS
        msg["To"] = to

        for file_path in file_paths:
            # Attach the file to the HTML
            with open(file_path, mode='rb') as bFile:
                # Get the filename alone
                filename = os.path.split(file_path)[1]
                # Create an attachment
                file = MIMEApplication(bFile.read(), _subtype=filename.split('.')[1])
                file.add_header('Content-Disposition','attachment', filename=filename)
                msg.attach(file)

        html = """\
        <html>
        <body>
            <p>Hi user! Here's your requested certificate signed by us! Enjoy your day</p>
            <p> Feel free to <strong>let us</strong> how you found our service</p>
            
        </body>
        </html>
        """
        part = MIMEText(html, "html")
        msg.attach(part)

        # Send the message
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(self.__EMAIL_ADDRESS, self.__EMAIL_PASSWD)
            # smtp.send_message(msg)
            smtp.sendmail(self.__EMAIL_ADDRESS, to, msg.as_string())
    
"""
The export from here to send files
"""
mail_service = Mail()

if __name__ == '__main__':
    ea = os.environ["EMAIL_ADDRESS"]
    ep = os.environ["EMAIL_PASSWD"]

    receiver = input("Enter receiver's address: ")
    content = input("The content for the mail: ")
    
    mail_object = Mail(ea, ep)
    mail_object.send_mail("Testing", receiver, content)