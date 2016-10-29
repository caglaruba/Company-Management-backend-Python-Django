from framework.util.multidict import MultiDict
from framework.util.cookiedict import CookieDict

from .constants import httpstatusforcode

class Response(object):

    def __init__(self):
        """Create a new empty Response object
        """
        
        # Set the default status to "200 OK"
        self._status = "200 OK"
        
        # The statuscode is also set to 200
        self._statuscode = 200
        
        # The body is initialized as a empty unicode string which should be utf-8 encoded
        self._body = ""
        self._charset = "utf-8"
        
        # The content-type is by default set to text/html
        self.content_type = "text/html"
        
        # The headers (this is a MultiDict because headers with the same key can occur)
        self.headers = MultiDict()

        # The cookies to be set are stored in a dictionary for each key a cookie will be created 
        # with the value
        self.cookies = CookieDict()
        
        # Set server data
        self.headers["Server"] = "Simplendi OpenSource Framework"
    

    def _getBody(self):
        return self._body
    
    def _setBody(self, data):
        self._body = data
       
    body = property(_getBody, _setBody,
    """The body is a readable and writable property.
    """)      

    def _getCharset(self):
        return self._charset
    
    def _setCharset(self, value):
        self._charset = value
    
    charset = property(_getCharset, _setCharset,
    """The charset is a readable and writable property.
    """)
    
    def _getContentLength(self):
        if self._charset:
            return len(self._body.encode(self._charset))
        else:
            return len(self._body)
    
    content_length = property(_getContentLength, None,
    """The content length is a read-only property
    """)
       
    def _setStatus(self, value):
        try:
            self._statuscode = int(value[0:3])
        except ValueError:
            raise ValueError("Non valid statuscode")
        self._status = value
        
    def _getStatus(self):
        return self._status
    
    status = property(_getStatus, _setStatus, None,
    """Status is a readable and writable string which should begin with three digits. The statuscode
    is modified on modification
    """)
    
    def _setStatusCode(self, value):
        try:
            self._statuscode = int(value)
        except ValueError:
            raise ValueError("Non valid statuscode")

        self._status = httpstatusforcode[self._statuscode]
            
    def _getStatusCode(self):
        return self._statuscode
    
    statuscode = property(_getStatusCode, _setStatusCode, None,
    """Statuscode is a readable and writable intereger. The status is modified for known statuscodes
    if a not know statuscode is used, use status
    """)
    
    def generateCookieHeaders(self):
        """Convert the cookies into Set-Cookie HTTP headers
        """
        for cookie_key in self.cookies:
            self.headers.append("Set-Cookie", self.cookies.getSetCookieHeader(cookie_key))
            
    def setJsonBody(self, body = None):
        """Set the content-type to json and optionally set the body
        """
        self.content_type = "application/json"
        if body:
            self.body = body
            
    def setRedirect(self, url, response_code = 302):
        self.statuscode = 302
        self.headers.append("Location", url)