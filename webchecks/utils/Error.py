import typing

class ValueError(BaseException):
	"""Input provided is invalid."""
	def __init__(self, msg : str):
		super(ValueError, self).__init__()
		self.args = (f"[ValueError] Invalid value provided: {msg}",)

class OptionsError(BaseException):
	"""Exception if an option was chosen that is not valid."""
	def __init__(self, fieldname : str, opts: tuple):
		super(OptionsError, self).__init__()
		self.args = (f"[OptionsError] Invalid option for {fieldname} chosen. Possible values include {args}.",)
		