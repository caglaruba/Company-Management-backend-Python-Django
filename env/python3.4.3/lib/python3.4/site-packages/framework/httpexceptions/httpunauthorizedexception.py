from .httpexception import HttpException

class HttpUnauthorizedException(HttpException):
    """Exception thrown when a 401 status code has to be returned
    """
       
    def __init__(self, reason = None):
        """Initialize a HttpNotFoundException
        """
        
        # Set status code
        self.statuscode = 401      
        
        # Set reason
        if not reason:
            reason = ""
        self.reason = reason