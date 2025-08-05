from typing import Any
import re

def camel_to_snake_case(text: str) -> str:
	"""
	Преобразует `CamelCase` в `snake_case`<br>
	```
	"CamelCase" => "camel_case"
	"MyHTTPResponse" => "my_http_response"
	"Weird_CamelCase" => "weird_camel_case"
	```
	"""
	return re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", '_', text).lower()


def _validate_positive_integer(valie: Any) -> None:
	"""
	Проверяет, что это целочисленное положительное число.

	:raise TypeError: Value isn't a integer.
	:raise ValueError: Value less than 1.
	"""

	if type(valie) is not int:
		raise TypeError(f'Value shall be a int type, but it\'s an {type(valie).__name__} type.')

	if valie < 1:
		raise ValueError(f'Value cannot be less than 1 (was given {valie}).')


def truncate_string(text: str, max_len: int, *, suffix: str = '...') -> str:
	"""
	Обрезает строку по указанной максимальной длине, ставит
	указанный суффикс вместо последних символов.

	Если строка была меньше длины суффикса и больше максимального
	размера, то вернётся обрезанный суффикс.
	"""
	_validate_positive_integer(max_len)

	if len(text) <= max_len:
		return text
	
	suffix_len: int = len(suffix)
	if suffix_len > max_len:
		# для оптимизации
		return suffix[:max_len]

	# 1. Обрезаем исходную строку по max_len
	# 2. Отрезаем сзади длину суффикса
	# 3. Подставляем суффикс
	# 4. Строка не могла получится больше максимального размера благодаря суффиксу,
	# так как если суффикс был больше максимальной длины - до сюда бы не дошло
	# благодаря проверке выше. А так надо было бы дописать [:max_len] в самом конце.
	truncated_text = f'{text[:max_len][:-suffix_len]}{suffix}'
	assert len(truncated_text) <= max_len, "Function is wrong!"

	return truncated_text
