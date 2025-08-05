import re
from django.core.exceptions import ValidationError

def string_is_numeric(value: str):
	if not isinstance(value, str):
		raise TypeError("Это не строка")

	try: int(value)
	except ValueError:
		raise ValidationError("Эта строка должна соответствовать целому числу")
