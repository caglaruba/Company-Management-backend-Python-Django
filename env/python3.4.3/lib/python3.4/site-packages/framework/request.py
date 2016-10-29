import cgi
import json
from urllib.parse import unquote_plus

from framework.util.acceptcontainer import AcceptContainer
from framework.util.multidict import MultiDict
from framework.util.cookiedict import CookieDict

class Request():
    
    def __init__(self, environment):
        """Create a Request object from the environment-dictionary.
        """
        
        # Store envirnment for futher reference
        self.environment = environment
        
        # Get REQUEST_METHOD (Required)
        self.method = environment['REQUEST_METHOD']
        
        # Get SERVER_PORT (Required)
        self.port = environment['SERVER_PORT']
        
        # Get HTTP_HOST (Optional)
        self.host = environment.get('HTTP_HOST')
        
        # Get SCRIPT_NAME (Can be empty)
        self.script_name = environment.get('SCRIPT_NAME', '')
        
        # Get PATH_INFO (Can be empty)
        self.path_info = environment.get('PATH_INFO','')
        
        # Get HTTP_USER_AGENT (Can be empty)
        self.user_agent = environment.get('HTTP_USER_AGENT', '')
        
        # Get HTTP_ACCEPT (Is AcceptContainer)
        self.accept = AcceptContainer(environment.get('HTTP_ACCEPT'))
        
        # Get HTTP_ACCEPT_LANGUAGE (Is AcceptContainer)
        self.accept_language = AcceptContainer(environment.get('HTTP_ACCEPT_LANGUAGE'))
        
        # Get HTTP_ACCEPT_ENCODING (Is AcceptContainer)
        self.accept_encoding = AcceptContainer(environment.get('HTTP_ACCEPT_ENCODING'))
        
        # Get HTTP_ACCEPT_CHARSET (Is AcceptContainer)
        self.accept_charset = AcceptContainer(environment.get('HTTP_ACCEPT_CHARSET'))
        
        # Get COOKIES
        self.cookies = CookieDict(environment.get('HTTP_COOKIE'))

        # Get CONTENT_LENGTH
        try:
            self.content_length = int(self.environment.get('CONTENT_LENGTH'))
        except:
            self.content_length = None

        # Get CONTENT_TYPE
        self.content_type = self.environment.get('CONTENT_TYPE', '')
        
        # Parse body
        self._parseBody()
        
        # Parse query
        self._parseQuery()
    
    def _parseBody(self):
        """Parses the body of the request into a dictionary. At the moment only 
        application/x-www-form-urlencoded is supported!
        """
        
        # If the content_type is defined and the content has a length try to parse the body
        if self.content_type and self.content_length:
            if self.content_type.startswith('application/x-www-form-urlencoded'):
                self.body = MultiDict()
                
                # Read the body from the virtual file
                body = self.environment["wsgi.input"].read(self.content_length)
                
                # Decode the body from its latin-1 decoding to a python string
                body = body.decode('latin-1')
                
                # Split the body into strings containing one key and one value
                pairs = body.split('&')
                
                # For each key value pair split it and decode it from urlencoded strings to a string
                for pair in pairs:
                    (key, _, value) = pair.partition('=');
                    
                    # Add key/value to MultiDict 
                    self.body.append(unquote_plus(key), unquote_plus(value))

            elif self.content_type.startswith("multipart/form-data"):
                self.body = cgi.FieldStorage(fp=self.environment["wsgi.input"], environ=self.environment)

            elif self.content_type.startswith("application/json"):
                if "charset" in self.content_type:
                    try:
                        charset = self.content_type[self.content_type.find("charset"):].rpartition("=")[2]
                    except:
                        charset = "UTF8"
                else:
                    charset = "UTF8"

                # Read the body from the virtual file
                body = self.environment["wsgi.input"].read(self.content_length)

                # Decode the body
                body = body.decode(charset)

                self.body = json.loads(body)
                
        elif self.content_length:
            self.body = self.environment["wsgi.input"].read(self.content_length)
        else:
            self.body = None

    def _parseQuery(self):
        """Parses the query strings that can be present in a request into a dictionary
        """
        
        self.query = MultiDict()
        
        # Get the query string
        query_string = self.environment.get("QUERY_STRING")
        
        # The seperator per key/value-pair is & so we split on that
        pairs = query_string.split('&')
        
        # Parse the key/value-string-pairs into a dictionary
        for pair in pairs:
            (key, _, value)  = pair.partition('=')
            
            # Add key/value to MultiDict
            self.query.append(unquote_plus(key), unquote_plus(value))
            
    def isGet(self):
        """Test to see if the request method is GET
        """
        return self.method == "GET"
    
    def isPost(self):
        """Test to see if the request method is POST
        """
        return self.method == "POST"
        
    def isJson(self):
        """Test to see if the request is a JSON request
        """
        return self.environment.get("HTTP_X_REQUESTED_WITH", "") == "XMLHttpRequest"
        
        
        
