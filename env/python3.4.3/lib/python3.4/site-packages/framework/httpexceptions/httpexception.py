class HttpException(Exception):
    """Exception that represents HttpExceptions
    """
    
    def __init__(self, statuscode, reason = None):
        """Initialize a HttpException with a statuscode and a option reason
        """
        
        # Set statuscode
        self.statuscode = statuscode
        
        # Set reason
        if not reason:
            reason = ""
        self.reason = reason
        
    def __str__(self):
        return self.__class__.__name__ + ": " + str(self.statuscode) + " " + self.reason
    
    def __repr__(self):
        return self.__str__()