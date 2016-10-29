from .httpexception import HttpException

class HttpBadRequestException(HttpException):
    """Exception that is used for invalid requests"""
    
    def __init__(self, reason = None):
        """Initialize a HttpException with a statuscode and a option reason
        """
        
        # Set statuscode
        self.statuscode = 400
        
        # Set reason
        if not reason:
            reason = ""
        self.reason = reason        