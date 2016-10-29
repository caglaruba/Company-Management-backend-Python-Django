from .request import Request
from .response import Response
from .session import Session
from .config import Config

class State():
    
    def __init__(self, environment, start_response):
        
        # Safe environment
        self._environment = environment
        
        # Safe start_response function to be called later
        self._start_response = start_response
        
        # Create a request-object out of the environment dictionary
        self.request = Request(environment)
        
        # Create a new response object
        self.response = Response()
                       
        # No session is created by default
        self.session = None
        
        
        
    def startResponse(self):
        """Start sending the response by generating the response headers and passing them through
        """
                
        # Generate cookie headers
        self.response.generateCookieHeaders()
        
        # Get already set headers
        headers = self.response.headers
        
        # Add the Content-Length header
        headers["Content-Length"] = str(self.response.content_length)
        
        # Add the Content-Type header with encoding parameter if present
        if self.response.charset:
            headers["Content-Type"] = (self.response.content_type + "; charset=" + self.response.charset)
        else:
            headers["Content-Type"] = self.response.content_type          
            
        # Convert the headers dictionary into a list of (key, value)
        header_list = headers.items()
     
        # Start the response by sending the status and the headers    
        self._start_response(self.response.status, header_list)
        
        
    def unfold(self):
        """Unfolds the state object into a request, response and session.
        """
        return (self.request, self.response, self.session)