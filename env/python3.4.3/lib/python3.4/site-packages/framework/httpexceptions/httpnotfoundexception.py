from .httpexception import HttpException

class HttpNotFoundException(HttpException):
    """Exception thrown when a 404 status code has to be returned
    """
    
    def __init__(self, reason = None):
        """Initialize a HttpNotFoundException
        """
        
        # Set status code
        self.statuscode = 404      
        
        # Set reason
        if not reason:
            reason = ""
        self.reason = reason