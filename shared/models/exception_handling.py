from logging import Logger, getLogger

from django.db.models		import Model
from django.db.utils		import OperationalError


_logger = getLogger(__name__)

class HandleAndLogNotMigratedModelError:
	"""
	Ловит исключение, возникающее если происходит обращение к модели, не прошедшей миграции.
	Логгирует в переданный логгер, иначе логирует в свой собственный, что будет менее информативно.

	Можно указать дополнительное, уточняющее сообщение для логгера, что следует из этой ошибки.<br>
	**По умолчанию:**<br>
	```
	Обнаружена попытка доступа к модели "{self._model.__name__}",
	для которой не проведены миграции.
	```
	**С комментарием:**<br>
	```
	Обнаружена попытка доступа к модели "{self._model.__name__}",
	для которой не проведены миграции, {error_comment}.
	```
	**Пример:**<br>
	```
	Обнаружена попытка доступа к модели "SiteSettings",
	для которой не проведены миграции, регистрация в админ-панели пропущена.
	```
	"""
	def __init__(
			self,
			model: type[Model],
			*,
			logger: Logger | None = None,
			error_comment: str | None = None):
		self._model = model
		self._logger = logger if logger else _logger

		# это удобнее чем всё сообщение целиком с %s для подстановки типа модели
		self._error_comment = error_comment 

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_value, traceback):
		if exc_type is not OperationalError:
			return False

		if not str(exc_value).startswith("no such"):
			_logger.debug(f"HandleAndLogNotMigratedModel Error: exc_value not startswith 'no such', exc_value: {exc_value}")
			return False

		self._logger.error(
			f'Обнаружена попытка доступа к модели "{self._model.__name__}", для которой не проведены миграции' +
			f", {self._error_comment}." if self._error_comment else '.'
		)
		return True
