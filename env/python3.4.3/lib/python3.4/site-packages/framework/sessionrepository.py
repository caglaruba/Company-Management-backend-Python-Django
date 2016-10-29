import json
from datetime import datetime

from .session import Session

class SessionRepository():
    
    def __init__(self, database_pool):
        """Initialize a SessionRepository with a DatabasePool
        """
        self._db_pool = database_pool
        
        
    def get(self, session_id):
        """Get a session by SessionID. If no session is found with session ID false is returned
        """
        cursor = self._db_pool.connect().cursor()
        
        # Query the session from the database, only searching for still valid sessions
        cursor.execute("SELECT id, data, expires FROM sessions WHERE id = %s and expires > %s", (session_id, datetime.utcnow()))
        
        # Get the first matching session
        result = cursor.fetchone()
        
        # Turn the result of the query into a session object
        if result:
            session = Session()
            session._id = result[0]
            session._data = json.loads(result[1])
            session._expires = result[2]
            session._stored = True
            return session        
        # Return None if no valid session is found.
        else:
            return None
            
    def add(self, session):
        """Add a session to the database
        """
        connection = self._db_pool.connect()
        cursor = connection.cursor()
        
        cursor.execute("INSERT INTO sessions (id, data, expires) VALUES (%s, %s, %s)", (session.id, json.dumps(session._data), session.expires))
        connection.commit()
        
    def save(self, session):
        """Save changes to a session into the database.
        """
        connection = self._db_pool.connect()
        cursor = connection.cursor()
        
        cursor.execute("UPDATE sessions SET data = %s, expires = %s WHERE id = %s", (json.dumps(session._data), session.expires, session.id))
        connection.commit()
        
    def clean(self):
        """Remove all expired sessions
        """
        connection = self._db_pool.connect()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM sessions WHERE expires <= NOW()")
        connection.commit()
        
        