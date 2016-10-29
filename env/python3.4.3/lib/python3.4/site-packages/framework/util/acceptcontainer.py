
class AcceptContainer():
    """AcceptContainer holds the values for the Accept-* HTTP-headers.
    """
    
    def __init__(self, accept_header_string):
        """Initialize a AcceptContainer object using a header string from an Accept-* header.
        """
        
        # Dictionary containing floats indicating quality factors for each mediatype (string as key)
        self.accepts = dict()
        
        # If a accept_header_string is provided parse it
        if accept_header_string:
            self.parse(accept_header_string)
            
            
    def parse(self, accept_header_string):
        """Parse the accept header string into the object
        """
        
        # Split the accept header string in the several acceptance parameters
        accept_params = accept_header_string.split(',')
        
        # For each accept_param get the quality factor
        for accept_param in accept_params:
            
            # Split the accept_param to see if a quality factor is present
            (key, _, quality_factor) = accept_param.partition(';')
                       
            if quality_factor:
                # Quality factor is present, parse it
                self.accepts[key] = float(quality_factor.partition('=')[2])
            else:
                # No quality factor present, so 1.0 is assumed per HTTP/1.1 specifications
                self.accepts[key] = 1.0