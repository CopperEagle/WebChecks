"""OptionsError class."""

class OptionsError(BaseException):
    """Exception if an option was chosen that is not valid."""
    def __init__(self, fieldname : str, opts: tuple):
        super(OptionsError, self).__init__()
        self.args = f"Invalid option for {fieldname} chosen. Possible values include {opts}."
