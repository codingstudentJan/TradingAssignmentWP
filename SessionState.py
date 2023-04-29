import streamlit as st

class SessionState:
    """
    Usage:
    To get or set session variables, you create an instance of the SessionState class and attribute the variables to it.
    In the example below, the variable 'count' is created and set to 0 when the SessionState instance is first created.
    On subsequent reruns of the script, the value of 'count' is retrieved from the SessionState instance.
    Example:
    >>> session_state = SessionState.get(count=0)
    >>> session_state.count += 1
    >>> st.write(session_state.count)
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @classmethod
    def get(cls, **kwargs):
        """
        Gets an existing SessionState instance or creates a new one if it doesn't exist.
        """
        if 'session' not in st.session_state:
            st.session_state.session = cls(**kwargs)
        return st.session_state.session
