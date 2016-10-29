import smtplib

from framework import Config

class EmailSender():
    """EmaiLSender can be used to send EmailMessage objects over SMTP/
    """
    
    def __init__(self):
        """Initialze the sender.
        """
        pass
        
    def send(self, email_message):
        """Send an email message over SMTP.
        """
        smtp_connection = smtplib.SMTP(Config()["smtp_server"])
        if Config().get("smtp_use_tls", None):
            smtp_connection.ehlo()
            smtp_connection.starttls()
            smtp_connection.ehlo()
        if Config().get("smtp_username", None):
            smtp_connection.login(Config()["smtp_username"], Config()["smtp_password"])
        smtp_connection.sendmail(email_message.from_address, email_message.to_address, email_message.getMessageString())
        smtp_connection.close()
    
    