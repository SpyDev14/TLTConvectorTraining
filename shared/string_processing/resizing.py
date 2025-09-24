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


def truncate_string(text: str, max_len: int, *, postfix: str = '...') -> str:
	"""
	Обрезает строку по указанной максимальной длине, ставит
	указанный постфикс вместо последних символов.

	Если по каким-то причинам, длина строки была меньше длины постфикса и больше максимального
	размера, вернётся обрезанный постфикс.
	"""
	_validate_positive_integer(max_len)

	if len(text) <= max_len:
		return text

	suffix_len: int = len(postfix)
	if suffix_len > max_len:
		return postfix[:max_len]

	# 1. Обрезаем исходную строку по max_len
	# 2. Отрезаем сзади длину постфикса
	# 3. Подставляем постфикс
	# 4. Строка не могла получится больше максимального размера из-за постфикса,
	# благодаря проверке выше.
	truncated_text = f'{text[:max_len][:-suffix_len]}{postfix}'
	assert len(truncated_text) <= max_len, "Function is wrong!"

	return truncated_text
