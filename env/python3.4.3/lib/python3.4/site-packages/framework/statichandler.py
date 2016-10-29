import mimetypes

from framework.httpexceptions import HttpNotFoundException

class StaticHandler():
    """StaticHandler handles request to static files and serves these files.
    """
    
    def __init__(self, folder):
        """Create new StaticHandler, point it to the base folder to search files in
        """
        self._folder = folder
        
        # If the path doesn't end with an "/" add one.
        if not self._folder.endswith("/"):
            self._folder += "/"
    
    def handle(self, state):
        """Handles a request to a static file. Serves the file
        """
        (request, response, session) = state.unfold()
        
        try:
            # Try to open the file in binary mode
            file = open(self._folder + request.path_info, 'rb')
            
            # Try to guess the content type
            response.content_type = mimetypes.guess_type(self._folder + request.path_info)[0]

            # Set a default content type if no guess was found
            if not response.content_type:
                response.content_type = "application/octet-stream"
            
            # We write binary data so return no charset
            response.charset = None
            
            # Read the contents of the file to the body of the response
            response.body = file.read()
        except:
            raise HttpNotFoundException()
        else:
            file.close()
                
        return state