from shared.string_processing 	import camel_to_snake_case
from shared.reflection 			import typename

# TODO: Перенести функцию в __init__, импорты выше заменить на import shared
def make_context_name(obj: object | type) -> str:
	return camel_to_snake_case(typename(obj))
