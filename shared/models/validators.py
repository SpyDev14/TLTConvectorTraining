from typing import Any
import re

from django.utils.deconstruct 	import deconstructible
from django.core.exceptions 	import ValidationError
from django.template.loader 	import get_template
from django.template			import TemplateDoesNotExist


__all__ = (
	'BaseValidator', # Для аннотации
	'StringStartswith',
	'StringEndswith',
	'FullmatchRegexValidator',
	'string_is_numeric',
	'template_with_this_name_exists',
	'env_variable_name',
)

# Сначала, всё было на классах
# Потом оказалось что классы (обычные) нельзя - перевёл на функции
# Потом оказалось, что фабричные функции нельзя
# Вот так и появились отдельно функции, отдельно классы с декоратором @deconstructible
# (который я добавляю через метакласс чтобы не делать этого вручную каждый раз)
# И вообще вся вот эта параша с компонентными функциями (_raise_if_not_str, _string_fullmatch_regex)
# UPD: которые я уже убрал, но эхо осталось
# UPD 2: но валидаторы со сложной кастомной логикой без параметров тоже нужны,
# а исходные (_raise_if_not_str, _string_fullmatch_regex) я удалил и создал вместо них классы
# поэтому теперь в них мы создаём классы 💀 (стоит сделать наоборот)
# PS: Это чтобы не возникало вопросов "Почему так".

class DeconstructibleMeta(type):
	"""Метакласс, который автоматически применяет @deconstructible."""
	def __new__(cls, name, bases, attrs):
		new_class = super().__new__(cls, name, bases, attrs)
		return deconstructible(new_class) # Декорируем класс

class BaseValidator(metaclass=DeconstructibleMeta):
	"""Все наследники автоматически @deconstructible."""
	error_msg = "Ошибка!"

	def __init__(self, *, invert: bool = False, **initkwargs):
		self.invert = invert

		for attr_name, value in initkwargs.items():
			if not hasattr(self, attr_name):
				raise AttributeError(f'У класса {self.__class__.__name__} нет атрибута {attr_name}!')
			setattr(self, attr_name, value)

	def _value_is_valid(self, value: Any) -> bool:
		return True

	def check_is_valid(self, value: Any) -> bool:
		is_valid = self._value_is_valid(value)
		if self.invert:
			is_valid = not is_valid
		return is_valid

	def build_error_msg(self, value: Any) -> Any:
		return self.error_msg

	def __call__(self, value: Any):
		if not self.check_is_valid(value):
			raise ValidationError(
				self.build_error_msg(value)
			)

class TargetValueTypeMixin:
	# Выбрал бы set, но isinstance работает с tuple
	allowed_value_types: tuple[type, ...] = ()

	def __call__(self, value):
		if not self.allowed_value_types:
			raise ValueError("Установите разрешённые типы для проверки!")

		if not isinstance(value, self.allowed_value_types):
			allowed_types = self.allowed_value_types
			actual_type = type(value)
			msg = None
			if len(allowed_types) == 1:
				expected = allowed_types[0].__name__
				msg = f"Expected {expected}, got {actual_type}"
			else:
				expected = ", ".join(t.__name__ for t in allowed_types)
				msg = f"Expected one of: {expected}, got {actual_type}"

			raise TypeError(msg)

		_super = super()
		if hasattr(_super, '__call__'):
			_super.__call__(value)


class BaseStringValidator(TargetValueTypeMixin, BaseValidator):
	allowed_value_types = (str, )

	def __init__(self, check_string: str, *, invert = False, **initkwargs):
		super().__init__(invert=invert, **initkwargs)
		self.check_string = check_string

	# Для аннотации                 vvv
	def _value_is_valid(self, value: str):
		return super()._value_is_valid(value)

class StringEndswith(BaseStringValidator):
	def build_error_msg(self, value):
		return f'Строка {"не" if self.invert else ""} должна заканчиваться на "{self.check_string}"!'

	def _value_is_valid(self, value):
		return value.endswith(self.check_string)

class StringStartswith(BaseStringValidator):
	def build_error_msg(self, value):
		return f'Строка {"не" if self.invert else ""} должна начинаться на "{self.check_string}"!'

	def _value_is_valid(self, value):
		return value.startswith(self.check_string)

# По итогу всё вернулось к истокам, но уже в изменённом виде
class FullmatchRegexValidator(TargetValueTypeMixin, BaseValidator):
	"""Проверяет, что вся строка соответствует переданному regex"""
	allowed_value_types = (str, )
	check_regex: str = r'[\s\S]*' # Что угодно по умолчанию
	error_msg = f"Строка не соответствует r'^{check_regex}$'"

	def __init__(self, check_regex, *, invert=False, **initkwargs):
		super().__init__(invert=invert, **initkwargs)
		self.check_regex = check_regex

	def _value_is_valid(self, value):
		return re.fullmatch(f"^{self.check_regex}$", value) is not None


# MARK: В виде функций
# (конкретные проверки)
def _raise_if_not_str(value):
	# Какое-то "спорное решение", скажем так
	# TODO: Сделать наоборот, проверяющую функцию и в классе
	# вызывать её с сохранёнными параметрами, а не наоборот
	class _check(TargetValueTypeMixin): allowed_value_types = (str, )
	_check()(value)


def string_is_numeric(value: str):
	_raise_if_not_str(value)
	try: int(value)
	except:
		raise ValidationError(
			"Эта строка должна соответствовать целому числу"
		)

def template_with_this_name_exists(value: str):
	_raise_if_not_str(value)
	if not value:
		return
	try:
		get_template(value)
	except TemplateDoesNotExist:
		raise ValidationError("Темплейта с таким именем не существует!")

def env_variable_name(value: str):
	FullmatchRegexValidator(
		r'[A-Z_][A-Z0-9_]+',
		error_msg = "Это некорректное имя ENV переменной!"
	)(value)

# Делал ИИ, я на это почти не потратил времени
def map_coordinates_format(value: str):
	_raise_if_not_str(value)
	# Проверка общего формата с помощью регулярного выражения
	pattern = r'^-?\d+\.\d+,\s-?\d+\.\d+$'

	FullmatchRegexValidator(
		check_regex = pattern,
		error_msg = 'Координаты должны быть в формате: "число.дробная_часть, число.дробная_часть"',
	)(value)

	# Извлечение и проверка числовых значений
	lat_str, lon_str = value.split(', ')
	try:
		lat = float(lat_str)
		lon = float(lon_str)
	except:
		# Хотя базовый regex и так гарантирует, что это будет число,
		# но технически он может и не покрыть некоторые кейсы
		raise ValidationError('Широта или долгота представлена некорректным числом')

	# Проверка допустимых диапазонов
	if not (-90 <= lat <= 90):
		raise ValidationError('Широта должна быть от -90 до 90')

	if not (-180 <= lon <= 180):
		raise ValidationError('Долгота должна быть от -180 до 180')
