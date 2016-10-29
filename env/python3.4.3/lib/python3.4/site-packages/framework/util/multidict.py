class MultiDict():
    """MultiDict is a special dict which can contain multiple ordered values per key
    """
    
    def __init__(self):
        self._items = {}
        
    def __getitem__(self, key):
        """Implements the operation which is called when a lookup with brackets is done:
        var = multidict[key]. This operation returns the first occurrence of a key.
        Throws KeyError if the key is not found.
        """
        values = self._items.get(key)
        
        if values:
            return values[0]
        else:
            raise KeyError(key)
        
    def __setitem__(self, key, value):
        """Implements the operation which is called when setting with brackets is done:
        multidict[key] = var. This operation changes the first occurrence of a key if present and 
        creates one otherwise.
        """      
        values = self._items.get(key)
        if not values:
            self._items[key] = []
            self._items[key].append(value)
        self._items[key][0] = value
        
        return
    
    def __delitem__(self, key):
        """Implements the operation which is called when a key is deleted. Deletes the first value
        if present, otherwise a KeyError is thrown
        """     
        values = self._items.get(key)
        
        if values:
            del values[0]
        else:
            raise KeyError(key)
            
    def __len__(self):
        """Gets the total amount of values
        """
        count = 0
        
        for (_, values) in self._items.items():
            count = count + len(values)
        
        return count
    
    def __iter__(self):
        """Iterate each key
        """     
        for key in self._items:
                yield key
                
    def __contains__(self, key):
        """Returns true if a item with key is in the multidict
        """
        if self.get(key) != None:
            return True
        else:
            return False
                
    def iteritems(self):
        """Generate a iterator of (key, value) pairs
        """
        for (key, values) in self._items.items():
            for value in values:
                yield (key, value)
                
    def items(self):
        """Return all items in the multdict as (key, value)
        """
        return [(key, value) for (key, value) in self.iteritems()]
    
    def occurences(self, key):
        """ Counts the amount of occurrences of a key
        """
        
        return len(self._items.get(key)) 
    
    def get(self, key, default = None):
        """Safely gets the first value for a key, default if the key isn't found
        """
        try:
            return self[key]
        except KeyError:
            return default
        
    def getAll(self, key):
        """Returns all values for a certain key
        """
        return self._items.get(key, [])

    def getlist(self, key):
        """Return all values for a certain key
        """
        return self._items.get(key, [])
        
    def append(self, key, value):
        """Appends a value for the key"""
        
        if not self._items.get(key):
            self._items[key] = []
        
        self._items[key].append(value)

        

            
    
    