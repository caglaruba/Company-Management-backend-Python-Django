import json
import uuid
from datetime import datetime

from framework import Config
from framework.session import Session

from models.storedsession import StoredSession


class SessionRepository():
    def __init__(self):
        config = Config()
        self.database_session_maker = config["database_session_maker"]

    def get(self, session_id):
        """Get a session by SessionID. If no session is found with session ID false is returned
        """

        database_session = self.database_session_maker()

        stored_session = database_session.query(StoredSession).filter(StoredSession.id == str(session_id)).first()

        database_session.close()

        # Turn the result of the query into a session object
        if stored_session:
            session = Session()
            session._id = uuid.UUID(stored_session.id)
            session._data = json.loads(stored_session.data)
            session._expires = stored_session.expires
            session._stored = True
            return session
        # Return None if no valid session is found.
        else:
            return None

    def add(self, session):
        """Add a session to the database
        """
        database_session = self.database_session_maker()

        stored_session = StoredSession()
        stored_session.id = str(session._id)
        stored_session.data = json.dumps(session._data)
        stored_session.expires = session._expires

        database_session.add(stored_session)
        database_session.commit()
        database_session.close()

    def save(self, session):
        """Save changes to a session into the database.
        """
        database_session = self.database_session_maker()

        stored_session = database_session.query(StoredSession).filter(StoredSession.id == str(session._id)).first()

        # Turn the result of the query into a session object
        if stored_session:
            stored_session.id = str(session._id)
            stored_session.data = json.dumps(session._data)
            stored_session.expires = session._expires

            database_session.add(stored_session)
            database_session.commit()
        database_session.close()


    def clean(self):
        """Remove all expired sessions
        """
        database_session = self.database_session_maker()
        database_session.query(StoredSession).filter(StoredSession.expires <= datetime.utcnow()).delete()
        database_session.commit()
        database_session.close()