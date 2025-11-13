"""StateStore - in-memory session state container."""


class StateStore(dict):
    """In-memory session state container.
    
    Inherits from dict to provide dictionary-like interface.
    State is not persisted and only exists during the current session.
    """
    pass

