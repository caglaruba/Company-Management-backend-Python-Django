import uuid
from datetime import datetime
from datetime import timedelta

class Session():
    """Session classes instances are used to store sessions. A session behaves like a dictionary; 
    data is stored by key. 
    """
    
    def __init__(self):
        """Create a new Session object. This autogenerates a random UUID session id and an expiry 
        time
        """
        
        # Session ID
        self._id = uuid.uuid4()
        
        # A dictionary to store session data
        self._data = dict()
        
        # Expires stores the time the session will expire. Default is 1 hour
        self._expires = datetime.utcnow() + timedelta(hours = 1)
        
        # The boolean changed is used to prevent unnecessary saving of the session
        self._changed = False
        
        # The boolean stored is used to indicaed wheter a session is stored
        self._stored = False

        
    def __getitem__(self, key):
        """Get the value stored in the session at key.
        Throws KeyError if the key doesn't exist.
        """
        return self._data[key]
        
    def __setitem__(self, key, value):
        """Change the value stored in the session at key to value.
        """
        self._data[key] = value
        self._changed = True
            
    def __delitem__(self, key):
        """Delete data stored behind key from the session.
        Throws KeyError if the key doesn't exist.
        """
        del self._data[key]
        self._changed = True
        
    def __contains__(self, key):
        """Returns true if data is in the session at key.
        """
        return key in self._data
    
    def get(self, key, default = None):
        """Safely try to get a value from the session at a key. When the key is not found it returns
        default.
        """
        try:
            return self[key]
        except KeyError:
            return default
        
    def isChanged(self):
        """Returns True if the session changed after creation, False otherwise.
        """
        return self._changed  
    
    def isStored(self):
        """Returns True if the session is stored somewhere.
        """
        return self._stored
        
    def _getID(self):
        return self._id
    
    id = property(_getID, None, None, 
    """This property contains the Session ID as UUID object. The property is read-only.
    """)
      
        
    def _getExpires(self):
        return self._expires
    
    def _setExpires(self, expires):
        self._expires = expires
        self._changed = True
        
    expires = property(_getExpires, _setExpires, None, 
    """This property contains the expiry time as datetime object. This property supports read and write.
    """)
    
    def setSessionLifetime(self, hours):
        """Set the session expiry on now+hours
        """
        expires = datetime.utcnow() + timedelta(hours = hours)
        self.expires = expires
    
    
            
        