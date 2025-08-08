from typing import Any


def _validate_positive_integer(value: Any) -> None:
	"""
	Проверяет, что это целочисленное положительное число.

	:raise TypeError: Value isn't a integer.
	:raise ValueError: Value less than 1.
	"""

	if type(value) is not int:
		raise TypeError(f'Value shall be a int type, but it\'s an {type(value).__name__} type.')

	if value < 1:
		raise ValueError(f'Value cannot be less than 1 (was given {value}).')


def truncate_string(text: str, max_len: int, *, suffix: str = '...') -> str:
	"""
	Обрезает строку по указанной максимальной длине, ставит
	указанный суффикс вместо последних символов.

	Если по каким-то причинам, длина строки была меньше длины суффикса и больше максимального
	размера, то вернётся обрезанный суффикс.
	"""
	_validate_positive_integer(max_len)

	if len(text) <= max_len:
		return text

	suffix_len: int = len(suffix)
	if suffix_len > max_len:
		return suffix[:max_len]

	# 1. Обрезаем исходную строку по max_len
	# 2. Отрезаем сзади длину суффикса
	# 3. Подставляем суффикс
	# 4. Строка не могла получится больше максимального размера из-за суффикса,
	# благодаря проверке выше.
	truncated_text = f'{text[:max_len][:-suffix_len]}{suffix}'
	assert len(truncated_text) <= max_len, "Function is wrong!"

	return truncated_text
