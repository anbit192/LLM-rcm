class UserSession:
    _instance = None

    def __init__(self):
        self._current_user = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_user(self, user):
        self._current_user = user

    def get_user(self):
        return self._current_user

    def is_logged_in(self):
        return self._current_user is not None