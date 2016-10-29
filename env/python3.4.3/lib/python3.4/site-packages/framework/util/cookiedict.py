from datetime import datetime

class CookieDict():
    """CookieDict is used for storing cookies from HTTP-requests and -responses.
    """
    
    # Store cookies as dict in a dict:
    # ["value"] = Value
    # ["expires"] = Expires
    # ["domain"] = Domain
    # ["path"] = Path
    # ["secure"] = Secure
    # ["httponly"] = HttpOnly
    
    def __init__(self, cookie_header = None):
        """Initialize a cookie dictionary for storing cookies and their values. This is a extension 
        of a normal dictionary, it can also store the attributes for cookies.
        """
        self._cookies = dict()
        
        if cookie_header:
            self.readCookieHeader(cookie_header)        
        
    def _newCookie(self, key):
        """Generate a new cookie at key.
        """
        self._cookies[key] = dict()
        self._cookies[key]["value"] = ""
        self._cookies[key]["expires"] = None
        self._cookies[key]["domain"] = None
        self._cookies[key]["path"] = None
        self._cookies[key]["secure"] = False
        self._cookies[key]["httponly"] = False
        
    def __getitem__(self, key):
        """Get value for cookie with key.
        """
        return self._cookies[key]["value"]
    
    def __setitem__(self, key, value):
        """Set value for cookie with key.
        """
        if not key in self._cookies:
            self._newCookie(key)
        self._cookies[key]["value"] = value
    
    def __delitem__(self, key):
        """Delete cookie with key.
        """
        del self._cookies[key]
    
    def __len__(self):
        """Return the amount of cookies.
        """
        return len(self._cookies)
    
    def __contains__(self, key):
        """Returns true if a cookie with key is present
        """
        return key in self._cookies
    
    def __iter__(self):
        """Iterate over keys.
        """
        for key in self._cookies:
            yield key
            
    def iteritems(self):
        """Iterate over keys and values.
        """
        for key in self._cookies:
            yield (key, self._cookies[key]["value"])
    
    def getDomain(self, key):
        """Get the base domain for cookie with key.
        """
        return self._cookies[key]["domain"]
        
    def setDomain(self, key, value):
        """Set the base domain for cookie with key.
        """
        self._cookies[key]["domain"] = value
        
    def getPath(self, key):
        """Get the path for cookie with key.
        """
        return self._cookies[key]["path"]
    
    def setPath(self, key, value):
        """Set the path for cookie with key.
        """
        self._cookies[key]["path"] = value
    
    def getSecure(self, key):
        """Get the secure attribute for cookie with key.
        """
        return self._cookies[key]["secure"]
    
    def setSecure(self, key, value):
        """Set the secure attribute for cookie with key.
        """
        self._cookies[key]["secure"] = value
    
    def getHttpOnly(self, key):
        """Get the HTTP-only attribute for cookie with key.
        """
        return self._cookies[key]["httponly"]
    
    def setHttpOnly(self, key, value):
        """Set the HTTP-only attribute for cookie with key.
        """
        self._cookies[key]["httponly"] = value
        
    def getExpires(self, key):
        """Get the expires attribute for cookie with key.
        """
        return self._cookies[key]["expires"]
    
    def setExpires(self, key, value):
        """Set the expires attribute for cookie with key.
        """
        self._cookies[key]["expires"] = value
        
    def expireNow(self):
        """Expire the cookie now
        """
        self._cookies[key]["expires"] = datetime(year = 1900, month = 1, day = 1)
        
    def readCookieHeader(self, cookie_header):
        """Read a cookie header from a request into the CookieDict.
        """      
        # Split the contents of the Cookie header into a array of strings, one for each cookie
        cookies = cookie_header.split('; ')
            
        # Parse each cookie string into a key and value
        for cookie in cookies:
            (key, _, value) = cookie.partition('=')
                
            # Set value for each cookie
            self[key] = value
        
    def getSetCookieHeader(self, key):
        """Return a string for a Set-Cookie HTTP header for cookie with key.
        """
        
        # Raise a key error for a non existant key
        if key not in self:
            raise KeyError(key)
        
        # Add key
        header_string = key
        
        # Add = sign
        header_string += "="
        
        # If the value is a not a string, turn it in a latin-1 string.
        if isinstance(self[key], str):
            header_string += self[key]
        else:
            header_string += self[key].decode('latin-1')

        # Create attributes if they are set
        if self.getExpires(key):
            header_string += "; Expires=" + self.getExpires(key).strftime('%a, %d %b %Y %H:%M:%S GMT')       
        if self.getHttpOnly(key):
            header_string += "; HttpOnly"
        if self.getSecure(key):
            header_string += "; Secure"
        if self.getDomain(key):
            header_string += "; Domain=" + self.getDomain(key)
        if self.getPath(key):
            header_string += "; Path=" + self.getPath(key)
            
        return header_string
        