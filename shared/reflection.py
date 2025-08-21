def typename(obj: object | type) -> str:
	"""
	Возвращает название типа (`type(obj).__name__` / `obj.__name__`)
	"""
	if isinstance(obj, type):
		return obj.__name__
	return type(obj).__name__
