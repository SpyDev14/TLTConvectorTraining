from shared.string_processing 	import camel_to_snake_case
from shared.reflection 			import typename

# NOTE: Может сообразить что-то получше такого модуля?
# Можно перенести в shared, но пока нигде кроме как в
# bases оно не используется.

def make_context_name(obj: object | type) -> str:
	return camel_to_snake_case(typename(obj))
