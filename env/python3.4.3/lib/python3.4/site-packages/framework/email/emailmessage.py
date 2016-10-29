from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

class EmailMessage():
    """EmailMessage represents an email message. This class can be used to send emails using the EmaiLSender
    """
    
    
    def __init__(self):
        """Initialize an empty message.
        """
        self.to_address = ""
        self.from_address = ""
        self.subject = ""
        self.body = ""        
        
    def getMIMEObject(self):
        """Get a MIME-object representing the email message.
        """
        message = MIMEMultipart()
        message["From"] = self.from_address
        message["To"] = self.to_address
        message["Subject"] = self.subject.encode("ascii", "replace").decode("ascii")
        message.attach(MIMEText(self.body, "html", "utf-8"))
        
        return message
                       
    def getMessageString(self):
        """Get a string used for sending email data over SMTP-connections.
        """
        return self.getMIMEObject().as_string()