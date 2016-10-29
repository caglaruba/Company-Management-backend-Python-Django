class Config():
    
    # A class global variable is created so instances of config share the same data
    _variables = dict()
    
    def __init__(self):
        """Initialize a Config instance, all config instaces share the same data.
        """
        pass
    
    def __getitem__(self, key):
        """Get a item of the config via a dictionary-like method
        """
        return self._variables[key]
    
    def __setitem__(self, key, value):
        """Set a item of the config via a dictionary-like method
        """
        self._variables[key] = value
        
    def get(self, key, default):
        """Safely get a item of the config via a dictionary-like method
        """
        return self._variables.get(key, default)
 
    