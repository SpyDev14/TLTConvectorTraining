from importlib	import import_module
from logging 	import getLogger

from django.contrib.admin 	import ModelAdmin, site
from django.db.models 		import Model
from django.conf 			import settings
from django.apps 			import apps

from shared.console.ansi_codes 	import *
from shared.reflection 			import typename


_logger = getLogger(__name__)

# Задавать в DEFAULT_MODEL_ADMIN_CLASSES в настройках, подробнее в документации
# AdminModelRegister.
# Тем не менее, если указать Model: CustomModelAdmin - это сработает.
_default_admin_classes_for_models: dict[type[Model], type[ModelAdmin]] = { }
_defaults_loaded: bool = False

def _get_default_admin_class_for_model(model_class: type[Model]) -> type[ModelAdmin] | None:
	for cls in model_class.mro():
		if not issubclass(cls, Model):
			break
		if cls in _default_admin_classes_for_models:
			return _default_admin_classes_for_models[cls]

	return None


def _set_default_admin_class_for_model_subclasses(model_class: type[Model], admin_class: type[ModelAdmin]):
	"""
	Устанавливает переданный подкласс `ModelAdmin` для подклассов
	указанной модели как admin class по умолчанию.

	Raises:
		TypeError:
			- Класс модели не является подклассом `Model`
			- Admin class не является подклассом `ModelAdmin`
		RuntimeError:
			- Уже зарегистрированно
	"""
	if not issubclass(model_class, Model):
		raise TypeError("Model class shoud be a subclass of Model")

	if not issubclass(admin_class, ModelAdmin):
		raise TypeError("Model admin class shoud be a subclass of ModelAdmin")

	if model_class in _default_admin_classes_for_models:
		# Для явности. Если нужно будет переопределять - сделаю отдельный метод.
		raise RuntimeError("Already registered")

	_default_admin_classes_for_models[model_class] = admin_class
	_logger.debug(
		f"admin class {L_GREEN}{admin_class.__qualname__}{RESET} succesfully setted "
		f"as default admin class for subclasses of {L_GREEN}{typename(model_class)}{RESET}."
	)


def _load_default_admin_classes_for_models():
	"""
	Загружает стандартные админ-классы для моделей из настроек
	проекта, из поля `DEFAULT_MODEL_ADMIN_CLASSES`.

	### Пример использования:
	- **settings.py**
	```
	DEFAULT_MODEL_ADMIN_CLASSES = {
		'solo.models.SingletonModel': 'solo.admin.SingletonModelAdmin'
	}
	```
	Теперь все `SingletonModel` в админке по умолчанию будут
	регистрироваться под `SingletonModelAdmin`.

	Raises:
		RuntimeError:
			- Уже загружено (повторный вызов)
	"""
	global _defaults_loaded
	if _defaults_loaded:
		raise RuntimeError('Already loaded')

	mapping: dict[str, str] = getattr(settings, 'DEFAULT_MODEL_ADMIN_CLASSES', {})

	for model_path, admin_path in mapping.items():
		# 'solo.models.SingletonModel' -> 'solo.models', 'SingletonModel'
		model_module, model_class_name = model_path.rsplit('.', 1)
		admin_module, admin_class_name = admin_path.rsplit('.', 1)

		model_class = getattr(import_module(model_module), model_class_name)
		admin_class = getattr(import_module(admin_module), admin_class_name)

		_set_default_admin_class_for_model_subclasses(
			model_class = model_class,
			admin_class = admin_class
		)

	_defaults_loaded = True


class AdminModelRegistrator:
	"""
	`AdminModelRegistrator` нужен для удобной автоматической регистрации моделей
	в Django-админке.

	<small><b>Админ-класс</b> - это класс, наследующийся от <code>ModelAdmin</code>, используемый
	для отображения модели в админ-панели.</small>
	<hr>

	Используйте `exclude_model` для исключения модели из списка для регистрации, либо
	`exclude_models` для множественного исключения.
	<hr>

	Используйте `set_custom_admin_class_for_model()` для установки кастомного админ-класса
	для конкретной модели, либо используйте версию-декоратор: `@set_for_model()`
	над кастомным админ-классом.
	<hr>

	**После определения моделей для регистрации и их админ-классов вызовите `register()`
	для произведения регистрации.**
	<hr>

	Добавьте в **settings.py** словарь (`dict`) с названием `DEFAULT_MODEL_ADMIN_CLASSES`
	с парами ключ-значение вида: `'$модуль.КлассМодели': '$модуль.АдминКласс'` чтобы задать
	админ-классы по умолчанию для указанных моделей и их подклассов.
	Ps: плохо работает с админками и моделями из наших приложений, нужно фиксить (ошибка -
	приложение ещё не загружено).
	(Пример ниже).
	<hr>

	### Пример использования:
	- **settings.py**
	```
	DEFAULT_MODEL_ADMIN_CLASSES = {
		'solo.models.SingletonModel': 'solo.admin.SingletonModelAdmin'
	}
	```
	- **models.py**
	```
	class MyModel(Model): ...
	class MySpecialModel(Model): ...
	class MyModelForExclude(Model): ...
	class MyModelForExcludeAlt(Model): ...
	class MySingletonModel(SingletonModel): ...
	```
	- **admin.py**
	```

	registrator = AdminModelRegistrator(
		app_name = MyAppConfig.name,
		# Рекомендуемый способ для исключения моделей
		exclude_models = {MyModelForExclude},
	)

	# Допустим, получили от куда-то из вне
	collected_models_for_exclude = {models.MyModelForExcludeAlt}
	registrator.exclude_models(collected_models_for_exclude)

	# Делаем что-то и поэтому нужно исключить конкретно эту модель
	registrator.exclude_model()
	class MySpecialModelInline(StackedInline):
		...

	# Нужна кастомная ModelAdmin
	@registrator.set_for_model(models.MyModel)
	class MyModelAdmin(ModelAdmin):
		inlines = [MySpecialModelInline]

	# Проводим регистрацию всех моделей из приложения MyApp
	# с учётом всех настроек
	registrator.register()
	```
	Теперь в нашей админке будут зарегистрированны все модели из приложения
	`my_app`, кроме `MyModelForExclude`, `MyModelForExcludeAlt` и `MySpecialModel`.
	`MyModel` будет зарегистрированна под `MyModelAdmin`, а `MySingletonModel`
	будет зарегистрированна под `SingletonModelAdmin`.
	"""
	def __init__(self,
			*,
			app_name: str,
			excluded_models: set[type[Model]] = set(),
			custom_admin_classes_for_models: \
				dict[type[Model], type[ModelAdmin]] = dict()):
		"""
		Params:
			app_name:
				Название приложения, с которым будет вестись работа.
				Указывайте название приложения в котором вы регистрируете модели.
				Рекомендуется делать это через `AppConfig.name`, вместо прямого
				указания названия.

			excluded_models:
				Исключённые из списка регистрации модели по умолчанию.

			custom_admin_classes_for_models:
				Кастомные `ModelAdmin` для конкретных моделей по умолчанию.
		"""
		self._app_name = app_name
		self._excluded_models = excluded_models
		self._custom_admin_classes_for_models = custom_admin_classes_for_models

		if not _defaults_loaded:
			_load_default_admin_classes_for_models()

	def exclude_model(self, model: type[Model]):
		"""Исключит модель из списка для регистрации."""
		self._excluded_models.add(model)

	def exclude_models(self, models: set[type[Model]]):
		"""Исключит модели из списка для регистрации."""
		self._excluded_models.update(models)

	def set_custom_admin_class_for_model(self, model: type[Model], admin_class: type[ModelAdmin]):
		"""Установит кастомную `ModelAdmin` для указанной модели."""
		self._custom_admin_classes_for_models[model] = admin_class

	def set_for_model(self, model: type[Model]):
		"""Установит класс ниже в качестве кастомной `ModelAdmin`
		для указанной модели."""
		def decorator(admin_class: type[ModelAdmin]):
			self.set_custom_admin_class_for_model(model, admin_class)
			return admin_class

		return decorator


	def register(self):
		"""
		Используйте для проведения регистрации моделей в самом конце модуля.
		Выбросит стандартное исключение о попытке повторной регистрации модели,
		если вы пытались зарегистрировать что-то вручную через `admin.site.register()`.

		Если вам действительно необходимо регистрировать какую-то модель вручную -
		пометьте её как исключённую из списка для регистрации.

		**ВНИМАНИЕ!** Если модель **НЕ ПРОШЛА МИГРАЦИИ** - она **ПРОЙДЁТ** регистрацию
		и попадёт в админ-панель! Учитывайте это и проводите миграции сразу же.<br>
		<small>Ps: ошибка возникнет только при переходе на страницу модели в админке.</small>
		"""
		_logger.debug('-' * 48)
		for model in apps.get_app_config(self._app_name).get_models():
			START_LOG_TEXT = (
				f"model {L_GREEN}{typename(model)}{RESET} "
				f"from {L_MAGENTA}{self._app_name}{RESET}"
			)
			if model in self._excluded_models:
				_logger.debug(f"{START_LOG_TEXT} is {L_RED}excluded{RESET}.")
				continue

			admin_class = ModelAdmin

			if model in self._custom_admin_classes_for_models:
				admin_class = self._custom_admin_classes_for_models[model]

			elif default_admin_class := _get_default_admin_class_for_model(model):
				admin_class = default_admin_class

			site.register(model, admin_class)
			_logger.debug(
				f"{START_LOG_TEXT} succesful registered with {L_GREEN}{typename(admin_class)}{RESET} admin class."
			)
