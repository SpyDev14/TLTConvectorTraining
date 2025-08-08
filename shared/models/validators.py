from pathlib import Path
from abc import ABC, abstractmethod
import re

from django.core.exceptions import ValidationError


class BaseStrValidator(ABC):
	@abstractmethod
	def validator(self, value: str) -> None:
		if not isinstance(value, str):
			raise TypeError("Это не строка")


class BaseRegexValidator(BaseStrValidator):
	"""Строка должна полностью соответствовать regex"""
	valid_regex: str = r"[\S\s]*"
	regex_validation_error_msg: str = f"Эта строка не соответствует regex: ^{valid_regex}$"

	@abstractmethod
	def validator(self, value):
		super().validator(value)

		valid: bool = re.fullmatch(f"^{self.valid_regex}$", value) is not None

		if not valid:
			raise ValidationError(self.regex_validation_error_msg)


class StringIsNumeric(BaseStrValidator):
	def validator(self, value):
		super().validator(value)

		try: int(value)
		except ValueError:
			raise ValidationError("Эта строка должна соответствовать целому числу")


class TemplateWithThisNameExists(BaseStrValidator):
	def validator(self, value):
		super().validator(value)

		if not Path(value).exists():
			raise ValidationError("Темплейта с таким именем не существует!")

# Можно было бы и обойтись, но у меня написание вот этого заняло 2 минуты
class EnvVariableName(BaseRegexValidator):
	valid_regex = r'[A-Z_][A-Z0-9_]+'
	regex_validation_error_msg = "Это некорректное имя ENV переменной!"


# class TelegramChatId(BaseStrValidator):
# 	class PublicChannel(BaseRegexValidator):
# 		valid_regex = r'@[a-z][a-z0-9_]{4,31}'
# 		regex_validation_error_msg = (
# 			'Это некорректный ID телеграмм чата! '
# 			'Он должен начинаться с @, разрешённые символы: [a-z] и [0-9], '
# 			'но первая буква не может быть цифрой,'
# 			'длина от 5 до 32 символов.'
# 		)

# 	class 


# 	def validator(self, value):
# 		super().validator(value)


