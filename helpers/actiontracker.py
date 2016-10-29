

class ActionTracker():
    permissions = None

    def __init__(self):
        self.permissions = []

    def add(self, permission_name):
        if permission_name not in self.permissions:
            self.permissions.append(permission_name)

    def list(self):
        return self.permissions[:]

