
import typing
from webchecks.utils.Error import ValueError

# primitive but makes stuff simpler
def input_check(pred : bool, msg : str):
	"""For given input checks if the predicate holds. If not, it will raise a ValueError."""
	if (not pred):
		raise ValueError(msg)