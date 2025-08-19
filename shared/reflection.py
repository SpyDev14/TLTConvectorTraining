def typename(obj: object | type) -> str:
	"""Возвращает название типа"""
	if isinstance(obj, type):
		return obj.__name__
	return type(obj).__name__
