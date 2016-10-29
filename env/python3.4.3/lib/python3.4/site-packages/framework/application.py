from functools import partial
from wsgiref.simple_server import make_server

from framework import State
from framework import Config
from framework.session import Session
from framework.httpexceptions import HttpException

class Application():
    """This class serves as a base for applications, each application class should be an instance
    of this class.
    """

    def __init__(self):
        """Initialize an Application.
        """             
        # This function will be called when an undefined exception is thrown after routing that isn't catched
        self.undefined_exception_handler = None      
         
        # The function with the corresponding status code will be called after routing if a HttpException is thrown if 
        # present in the dictionary. 
        self.http_code_routes = dict()
        
        # Create a session repository for storing and fetching sessions
        self._session_repository = None
                
    def __call__(self, state):
        """Handle a request which is already converted to an object. By default the controller is 
        called.
        """
        try:
            state = self.controller(state)
            return state
        
        # If a handler is available for HttpException with the statuscode, otherwise pass it to the 
        # next request handler
        except HttpException as httpexception:
            if httpexception.statuscode in self.http_code_routes:
                state = self.http_code_routes[httpexception.statuscode](state)
                return state
            else:
                raise httpexception
            
        # If a handler is available for undefined exceptions handle it, otherwise pass it to the
        # next request handler
        except Exception as exception:
            if self.undefined_exception_handler:
                state = self._handleUndefinedException(state, exception)
                return state
            else:
                raise exception
        
    def wsgi(self, environment, start_response):
        """WSGI-function to handle requests.
        """
        # Convert the environment to a state object
        state = State(environment, start_response)

        try:
            if self._session_repository:
                # Get session if available
                state.session = self._fetchSession(state)

            # Process the state by calling itself
            state = self(state)

            if self._session_repository:
                # Save session
                self._handleSession(state)

        # Handle any unhandled http exceptions
        except HttpException as exception:
            self._handleUnhandledHttpException(state, exception)

        # Start sending the response
        state.startResponse()

        # See what instance the body is
        if isinstance(state.response.body, (bytes,)):
            # body is a bytes-string don't encode it
            return [state.response.body]
        else:
            # body is a unicode-string encode it with the charset
            return [state.response.body.encode(state.response.charset)]

    def _handleUndefinedException(self, state, exception):
        """Handles a non-HTTP exception
        """
        (request, response, session) = state.unfold()

        # Run a controller function for undefined exceptions
        if self.undefined_exception_handler:
            state = self.undefined_exception_handler(state, exception)
        else:
            response.statuscode = 500
            response.body = ""
            
        return state

    def _handleUnhandledHttpException(self, state, httpexception):
        """
        Handles a HTTP exception that is not handled by any user defined code
        """
        (request, response, session) = state.unfold()

        response.statuscode = httpexception.statuscode

        try:
            response.body = httpexception.body
        except AttributeError:
            response.body = ""

        return state

 
    def _fetchSession(self, state):
        (request, response, session) = state.unfold()
        
        # Get Config to get variables
        config = Config()
        session_cookie_name = config["session_cookie"]
        session_lifetime = config["session_lifetime"] 
        
        # Check if a session id cookie is present
        if session_cookie_name in request.cookies:
            # Try getting the session from the database
            session = self._session_repository.get(request.cookies[session_cookie_name])
                
            # Return the session if one was found with the session id
            if session:
                return session

        # No SessionID is present create a new session
        session = Session()
            
        # Set session expiry
        session.setSessionLifetime(session_lifetime)
            
        # Nothing is really changed, so dismiss changed for now
        session._changed = False
            
        return session
    
    def _handleSession(self, state):
        (request, response, session) = state.unfold()
        
        if session.isChanged() and session.isStored():
            # Save the session
            self._session_repository.save(session)

        elif session.isChanged() and not session.isStored():
            # Add the session to the repository
            self._session_repository.add(session)
            
            # Set a cookie for the client to remember the session id
            state = self._createSessionCookie(state)
            
        return state        
    
    def _createSessionCookie(self, state):
        (request, response, session) = state.unfold()
                    
        # Get Config to get variables
        config = Config()
        session_cookie_name = config["session_cookie"]
        session_httponly = config["session_httponly"]
        session_secure = config["session_secure"]
        
        # Set the Session Cookie with it's parameters
        response.cookies[session_cookie_name] = str(session.id)
        response.cookies.setHttpOnly(session_cookie_name, session_httponly)
        response.cookies.setSecure(session_cookie_name, session_secure)
        response.cookies.setExpires(session_cookie_name, session.expires)
        response.cookies.setPath(session_cookie_name, "/")
        
        return state       
                        
             
    def getWsgi(self):
        """Return a WSGI-function that can be called without knowledge about the class
        """
        return partial(Application.wsgi, self)
    
    def serve(self, port=8000):
        """Serve the application via HTTP on a port (default 8000). Can be cancelled by stopping
        the process
        """
        
        # Make a HTTP-server from the WSGI-handler
        server = make_server('', port, self.wsgi)
        
        # Run the server until terminated
        server.serve_forever()
        
    
    