import re

from framework.statichandler import StaticHandler

from framework.httpexceptions import HttpException
from framework.httpexceptions import HttpNotFoundException

from framework.constants import httpmethods

class Router():
    """Router objects are used to define routes in. These routes can connect urls to functions and
    part of urls to applications such that a request is passed through to the function or
    application
    """
    
    def __init__(self):
        """Initialize a Router object
        """
            
        # Functions that will be called before (pre) and after (post) routing. The functions should
        # return a tuple (state, stop) where if stop is True routing will not be continued. 
        self.preroute = None
        self.postroute = None
        
        # Contains the routes defined. A route is a tuple containing:
        # (Forwarding?, Regular expression, Function for a mapping and application for forwarding, Allowed methods)
        self._routes = []
        
        
    def addMapping(self, regexp, function, methods = None):
        """Add a url to function mapping to the router. A regular expression is used to match the
        url. Groups can be used to pass strings as positional arguments to the function.
        """
        
        # If the methods are not limited, allow every HTTP method
        if not methods:
            methods = httpmethods
            
        # Add route to the route list
        self._routes.append((False, re.compile(regexp), function, methods))
        
    def addStaticMapping(self, regexp, folder, methods = None):
        """Adds a url to static files to the router. A regular expression is used to match the url.
        
        TODO: WIP
        """
        if not methods:
            methods = httpmethods
            
        static_handler = StaticHandler(folder)
            
        self._routes.append((True, re.compile(regexp), static_handler.handle, methods))
    
    def addForwarding(self, regexp, application, methods = None):
        """Ads a url to application mapping to the router. A regular expression is used to match the
        url. The matching part of the url is removed from the path_info.
        """
        
        # If the methods are not limited, allow every HTTP method
        if not methods:
            methods = httpmethods
            
        # Add route to the route list
        self._routes.append((True, re.compile(regexp), application, methods))
        
    def _changeRequestForForwarding(self, state, matched_prefix):
        """Changes the path_info and script_name for forwarding. This is done to give the apps 
        forwarded to the idea that they are on root.
        """
        
        # Create local reference to the request for shorter code
        request = state.request
        
        # If the script_name ends with an / strip it from the script_name because one will be added
        # after the current script_name from the matched_prefix 
        if request.script_name.endswith("/"):
            request.script_name = request.script_name[0:len(request.script_name)-1]
            
        # Add the matched prefix to the script_name
        request.script_name += matched_prefix
        
        # Remove the matched prefix from the path info 
        request.path_info = request.path_info[len(matched_prefix):len(request.path_info)]
        
        return state
        
    
    def route(self, state):
        """Route a state: First preroute is called if available. Then the first matching mapping
        or forwarding is searched. Afterwards postroute is called. 
        """        
        
        # Run preroute if available
        if self.preroute:
            (stop, state) = self.preroute(state)
            if stop:
                return state
           
        state = self._findroute(state)
                            
        # Run postroute if available
        if self.postroute:
            (stop, state) = self.postroute(state)
            if stop:
                return state
            
        return state
             
    
    def _findroute(self, state):
        """Internal function to find the first matching route and execute that route.
        """
                
        # Find first matching route
        for (forwarding, compiled_regexp, appfunc, methods) in self._routes:
            
            # See if the path info matches the reqular expression
            match = compiled_regexp.match(state.request.path_info)
            
            if match and state.request.method in methods:
                # See if we have to forward or not
                if forwarding:
                    # Set the path_info and script_name right: This is such that apps forwarded to
                    # have the idea they are on root.                  
                    state = self._changeRequestForForwarding(state, match.group(0))
                    
                    # Forward request to the app
                    return appfunc(state)
                else:
                    # Map request to function and pass variables that matched
                    return appfunc(state, *(match.groups()))
                
        # No match found raise a HTTP Not Found Exception
        raise HttpNotFoundException()
  
    
    def __call__(self, state):
        """Equivalent to route.
        """
        return self.route(state)
                