from functools 		import cached_property
from typing 		import Self
from os 			import getenv
import logging

from django.utils.safestring 	import mark_safe
from django.core.exceptions 	import ValidationError
from django.core.cache 			import cache
from django.urls 				import resolve, reverse, NoReverseMatch
from django.db 					import models

from tinymce.models 	import HTMLField
import requests

from shared.models.validators 	import *
from shared.models.managers 	import IndividualizedBulkOperationsManager
from shared.telegram.params 	import MessageParseMode
from shared.reflection 			import typename
from core.models.bases 			import BaseRenderableModel
# from core.views.bases 		import GenericPageView (circular import, locally imported in Page.clean())
from core.constants 			import RENDERING_SUPPORTS_TEXT
from core.config 				import TELEGRAM_SENDING

_logger = logging.getLogger(__name__)

# Можно добавить опциональную связь с другой моделью и добавлять список этих моделей в контекст темплейта
# для простых кейсов (т.е для маломальски уникальной логики создавать отдельный view)
# Но может быть и не стоит, это усложнение + могут возникнуть свои подводные камни
class Page(BaseRenderableModel):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.extra_context_manager: models.Manager['ExtraContext']

	is_generic_page = models.BooleanField('Это динамически-добавляемая страница?', default = False,
		help_text = mark_safe(
			'✅: Будет автоматически доступно по указанному url, требует заданного '
			'<code>template_name</code>. Используйте для простых страниц, не требующих своего View.<br>'
			'❌: Выбирайте, когда для обработки страницы нужно использовать кастомный view.<br>'
			'<br>'
			'Влияет на работу логики поля <code>URL path</code> & <code>template_name</code>.'))
	template_name = models.CharField('Название django-темплейта',
		# Проверяет только если поле заполнено
		validators = [template_with_this_name_exists],
		blank = True,
		# Ps: я знаю, что DetailView имеет функционал для получения темплейта из поля модели, но я не хочу,
		# чтобы было 2 разных способа задать темплейт - через модель и во View.
		# Также, усложнит понимание работы этого поля. Лучше в таких случаях всегда через View.
		help_text = mark_safe(
			'<code>is_generic_page:</code>✅ - Путь к файлу, включая расширение, <b>должно быть установленно</b>.<br>'
			'<code>is_generic_page:</code>❌ - Игнорируется, потому <b>должно быть</b> пустым.'))

	#                                                  страница на / будет по пути '' vvvv
	url_source = models.CharField("URL Source", max_length = 64, unique = True, blank = True,
		help_text = mark_safe(
			'<details style="padding-left: 1rem;">'
				'<summary style="margin-left: -1rem;"><code>is_generic_page</code>: ✅</summary>'
				'Полный URL путь, по которому будет доступна страница. Указав <code>info/about-us/</code> '
				'здесь, страница будет доступна по абсолютному пути <code>/info/about-us/</code><br>'
				'<code>get_absolute_url()</code> вернёт <code>"/info/about-us/"</code>.'
				'<br><b><u>Крайне рекомендуется</u></b> создавать url <u>на основе <code>slug</code></u>. '
				'Например, при slug = <code>about-us</code>, url = <code>info/about-us/</code>).<br>'
				'<br>'
			'</details>'
			'<details style="padding-left: 1rem;">'
				'<summary style="margin-left: -1rem;"><code>is_generic_page</code>: ❌</summary>'
				'View name того view, который обрабатывает эту страницу.<br>'
				'Например, в <code>urlpatterns</code> указан <code>path("fun-path/", ..., name="your-name")</code>, '
				'тут указываете <code>"your-name"</code>.<br>'
				'<code>get_absolute_url()</code> вернёт <code>"/fun-path/"</code>.'
			'</details>'
			'<br>'
			'Используется для получения url страницы в методе <code>get_absolute_url()</code>.<br>'
			'Также значение в этом поле валидируется и проходит проверку на корректность.'))
	content = HTMLField('Контент', blank = True, help_text = RENDERING_SUPPORTS_TEXT)

	class Meta:
		verbose_name = 'страница'
		verbose_name_plural = 'страницы'

	def clean(self):
		from core.views import GenericPageView

		# elif для читаемости
		if self.is_generic_page and not self.template_name:
			raise ValidationError({
				'template_name': 'template_name не может быть пустым при is_generic_page:✅'
			})
		if not self.is_generic_page and self.template_name:
			raise ValidationError({
				'template_name': 'Должно быть пустым при is_generic_page:❌ так как '
				'игнорируется (строгое обеспечение явности).'
			})

		# Проверка url_source
		try: self_url = self.get_absolute_url()
		except NoReverseMatch: raise ValidationError({
			'url_source': 'View с таким name не существует!'
		})
		if self.is_generic_page:
			validators: tuple[BaseValidator] = (
				StringStartswith('/', invert = True),
				StringEndswith('/')
			)
			for validator in validators:
				is_valid = validator.check_is_valid(self.url_source)

				if not is_valid: raise ValidationError({
					'url_source': validator.build_error_msg(self.url_source)
				})

			# Указано is_generic_page:✅, но также есть перекрывающий (конфликтующий)
			# view по такому же пути
			match = resolve(self_url)
			resolved_by_generic_view = getattr(match.func, 'view_class', None) is GenericPageView

			if not resolved_by_generic_view:
				view_f = match.func
				view_class = getattr(view_f, 'view_class', None)
				view_name = typename(view_class) if view_class else view_f.__name__
				raise ValidationError({
					'url_source': (
						f'Страница по URL "{self.get_absolute_url()}" перекрывается ' +
						f'{view_name}{'' if view_class else '() view'} ' +
						(f'(url name = {match.view_name})' if match.url_name else '') +
						' (логика работы при is_generic_page:✅).'
					)
				})


	def get_absolute_url(self):
		if self.is_generic_page:
			return f"/{self.url_source}"

		return reverse(self.url_source)

	# В контексте объект Page живёт только 1 запрос,
	# но внутри могут много раз обращаться к этому св-ву
	@cached_property
	def extra_context(self) -> dict:
		"""Для темплейтов"""
		return {ctx.key: ctx.value for ctx in self.extra_context_manager.all()}


class ExtraContext(models.Model):
	key = models.CharField('Ключ', max_length = 64)
	value = models.CharField('Значение')
	page = models.ForeignKey(Page, models.CASCADE, blank = True, null = True,
		related_name = 'extra_context_manager',
		verbose_name = 'Привязать к странице',
		help_text = mark_safe(
			'Если указать здесь страницу - ключ будет доступен через объект страницы '
			'и будет исключён из глобального контекста (<code>global.extra_context</code>).<br>'
			'Тем не менее, он всё также будет доступен глобально, но уже через <code>global.pages</code>'))

	class Meta:
		verbose_name = 'Дополнительный контекст'
		verbose_name_plural = 'Дополнительный контекст'

	def __str__(self):
		if self.page is None:
			return f'global {self.key}'
		else:
			return f'{self.key} for page "{self.page}"'


class TelegramSendingChannel(models.Model):
	class Specialization(models.TextChoices):
		NEW_REQUEST_NOTIFICATIONS = (
			'new_request_notifications', 'Уведомления о новых заявках')
		LOGS = ('logs', 'Логи')
		# Добавлять новые специализации тут

	token_env_name = models.CharField('ENV-переменная с токеном', validators = [env_variable_name],
		help_text = 'Название ENV переменной с токеном этого бота. '
		'Также проверяется существование токена в телеграм системе.')
	chat_id = models.CharField('ID чата', max_length = 32,
		help_text = 'Если был передан некорректный ID чата - ошибка возникнет только при '
		'первой попытке отправить сообщение, будте внимательны!')
	specialization = models.CharField('Специализация канала', choices = Specialization.choices,
		unique = True, help_text = "Может быть только один канал для конкретной специализации")

	# Стандартные bulk операции сломают встроенное кэширование.
	# Конечно, врядли кто-то в коде тут их будет делать, но в django есть встроенные операции
	# которые могут их неявно вызвать.
	objects = IndividualizedBulkOperationsManager()

	class Meta:
		verbose_name = 'Канал отправки сообщений в Telegram'
		verbose_name_plural = '📡 | Каналы отправки сообщений в Telegram'

	def __str__(self):
		return self.get_specialization_display()

	# Сменил кеширования с dict & lock на встроенное, по умолчанию всё также в пямяти
	@classmethod
	def _get_cache_key(cls, specialization: Specialization):
		return f"{typename(cls)}_for_{specialization}"

	@classmethod
	def _invalidate_cache(cls, specialization: Specialization):
		cache_key = cls._get_cache_key(specialization)
		cache.delete(cache_key)
		_logger.debug(f'Кешированный экземпляр {typename(cls)} для {specialization} был инвалидирован')

	def _to_cache_instance(self):
		cache_key = self._get_cache_key(self.specialization)
		cache.set(cache_key, self, timeout = None)
		_logger.debug(f'Экземпляр {typename(self)} для {self.specialization} был установлен в кеш')


	@classmethod
	def get_by_specialization(cls, specialization: Specialization) -> Self | None:
		"""Используется кэширование"""
		cache_key = cls._get_cache_key(specialization)
		instance = cache.get(cache_key)

		if instance:
			_logger.debug(f'Экземпляр {typename(cls)} для {specialization} был в кеше, возвращаем из него')
			return instance

		_logger.debug(f'Экземпляра {typename(cls)} для {specialization} нет в кеше, получение из БД')
		try:
			instance = cls.objects.get(specialization = specialization)
			instance._to_cache_instance()

		except cls.DoesNotExist:
			_logger.debug(f'Записи {typename(cls)} со специализацией {specialization} нет в БД')

		return instance

	def save(self, *args, **kwargs):
		if self.pk:
			old_specialization = type(self).objects.get(pk = self.pk).specialization

			if self.specialization != old_specialization:
				self._invalidate_cache(old_specialization)
			else:
				self._invalidate_cache(self.specialization)

		return super().save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		self._invalidate_cache(self.specialization)
		return super().delete(*args, **kwargs)


	@property
	def _token(self):
		return getenv(self.token_env_name, '')

	# Не кешируется так как может быть изменён в рантайме (название переменной модели)
	@property
	def token_env_set(self):
		"""Вернёт `False`, если env-переменной не существует, или была задана пустая строка."""
		return bool(self._token.strip())

	def _raise_if_token_not_set(self):
		if not self.token_env_set:
			raise RuntimeError(
				f'Token ENV variable with name {self.token_env_name}'
				' is not setted (not exsist or empty).'
			)

	# Если развивать идею, то можно в shared создать класс TelegramAPI,
	# принимающий токен в конструкторе, реализующий все методы telegram API
	# Хотя, вроде есть уже готовые библиотеки, с чистыми методами для API
	def _get_api_url(self, action: str):
		"""
		Возвращает полную url-строку с токеном и действием.
		Raises:
			RuntimeError: Токен не установлен в ENV переменную.
		"""
		self._raise_if_token_not_set()
		return f"https://api.telegram.org/bot{self._token}/{action}"

	def clean(self):
		if not self.token_env_set:
			raise ValidationError(
				'ENV переменная не установлена. Сначала добавьте её в .env-файл, потом указывайте здесь. '
				'Если вы её уже добавили в .env, то перезагрузите сервер.'
			)


	def send_message(
			self, text: str, *,
			parse_mode: MessageParseMode = MessageParseMode.HTML,
			timeout: float = TELEGRAM_SENDING.DEFAULT_SEND_MESSAGE_TIMEOUT):
		# Можно избежать блокировки потока, используя ASGI + async
		"""
		**ВНИМАНИЕ!!!** Блокирует поток выполнения!

		Raises:
			RuntimeError: Токен не установлен в ENV переменную.
			HTTPError: Статус ответа не был положительным (raise_for_status())
			RequestException: Во время запроса что-то пошло не так.
		"""
		url = self._get_api_url('sendMessage')
		payload = {
			'text': text,
			'chat_id': self.chat_id,
			'parse_mode': parse_mode.value # Можно без .value (StrEnum), но так понятней
		}

		response = requests.post(url, json = payload, timeout = timeout)
		response.raise_for_status()

	# IDEA: Можно написать кастомный декоратор, делающий try-функции, если
	# в проектах будет возникать слишком много шаблонного кода
	def try_send_message(
			self, text: str, *,
			parse_mode: MessageParseMode = MessageParseMode.HTML,
			**kwargs # Все остальные настройки не так часто используются
		) -> tuple[bool, Exception | None]:
		# Можно избежать блокировки потока, используя ASGI + async
		"""
		**ВНИМАНИЕ!!!** Блокирует поток выполнения.<br>
		Все параметры передаются в `send_message()`, kwargs тоже.
		"""

		# Не возвращаем response т.к при ошибке он будет в ex (если ошибка связана с сетью),
		# а при успехе он нам и не нужен
		try:
			self.send_message(text = text, parse_mode = parse_mode, **kwargs)
			return (True, None)
		except Exception as ex:
			return (False, ex)
