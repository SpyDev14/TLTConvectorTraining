from functools 		import cached_property
from threading 		import Lock
from typing 		import Self
from os 			import getenv
import logging

from django.utils.safestring 	import mark_safe
from django.core.exceptions 	import ValidationError
from django.core.cache 			import cache
from django.urls 				import resolve, Resolver404, ResolverMatch
from django.db 					import models

from tinymce.models 	import HTMLField
import requests

from shared.models.validators 	import *
from shared.models.managers 	import IndividualizedBulkOperationsManager
from shared.telegram.params 	import MessageParseMode
from core.models.bases 			import BaseRenderableModel
from core.constants 			import RENDERING_SUPPORTS_TEXT
from core.config 				import TELEGRAM_SENDING, GENERIC_TEMPLATE
# from core.views 				import GenericPageView (circular import, used in Page.clean())

_logger = logging.getLogger(__name__)

# Можно добавить опциональную связь с другой моделью и добавлять список этих моделей в контекст темплейта
# для простых кейсов (т.е для маломальски уникальной логики создавать отдельный view)
# Но может быть и не стоит, это усложнение + могут возникнуть свои подводные камни
class Page(BaseRenderableModel):
	extra_context_manager: models.Manager['ExtraContext']

	# WARN: Нейминг плохой, не отражает сути, пока нет идей как лучше
	is_generic_page = models.BooleanField('Это динамически-генерируемая страница?', default = False,
		help_text = mark_safe(
			'✅: Будет автоматически доступно по указанному url. Используйте для страниц без логики.<br>'
			'❌: Выбирайте, когда для обработки страницы нужно использовать кастомный view.<br>'
			'<br>'
			'Влияет на работу логики поля <code>URL path</code> & <code>template_name</code>.'))
	# TODO: Перевести на работу с url name при is_generic_page:❌
	# TODO: Alt: сменить систему получения page со сложной (относительно) url_path, на простой по slug
	# Если делать, то не забыть про проверку в clean()
	#                                                страница на / будет по пути '' vvvv
	url_path = models.CharField("URL путь", max_length = 64, unique = True, blank = True,
		validators = [StringStartswith('/', invert = True), StringEndswith('/')],
		help_text = mark_safe(
			'<details style="padding-left: 1rem;">'
				'<summary style="margin-left: -1rem;"><code>is_generic_page</code>: ✅</summary>'
				'URL путь, по которому будет доступна страница. Указав <code>info/about-us/</code> '
				'здесь, страница будет доступна по адресу <code>$site.$domain/info/about-us/</code>.'
				'<br><b><u>Крайне рекомендуется</u></b> создавать url <u>на основе slug</u>. '
				'Например, при slug = <code>about-us</code>, url = <code>info/about-us/</code>).<br>'
			'</details>'

			'<details style="padding-left: 1rem;">'
				'<summary style="margin-left: -1rem;"><code>is_generic_page</code>: ❌</summary>'
				'Название <b>должно</b> соответствовать адресу, по которому можно перейти на страницу '
				'по кастомному view.<br>'
				'При ненахождении страницы по указанному url - сохранить изменения / создать страницу '
				'не удастся.<br>'
			'</details>'

			'<br><b>Всегда</b> отражает реальный адрес страницы.'))
	# 29.08: Ранее не задумывался об этом. Решил, что в PageBasedView лучше задавать темплейт там же, в классе.
	template_name = models.CharField('Название django-темплейта',
		default = GENERIC_TEMPLATE.PAGE,
		validators = [template_with_this_name_exists],
		blank = True,
		help_text = mark_safe(
			'<code>is_generic_page:</code>✅ - Путь к файлу, включая расширение, <b>должно быть установленно</b>.<br>'
			'<code>is_generic_page:</code>❌ - Может быть пустым. Будет проигнорировано при работе '
			'с <code>PageBasedListView</code>.'))
	content = HTMLField('Контент', blank = True, help_text = RENDERING_SUPPORTS_TEXT)
		# Это работает вполне себе неплохо, только нужно знать как оно обработается под капотом.
		# Я тестил - всё гуд.
		# Но лучше использовать TinyMCE т.к CKEditor4 редактор максимально всра**ый.
		# К тому же, CKEditor4 устарел не только морально. Он больше неподдерживается и потенциально небезопасен.

		# UPD: Погуглил про CKEditor4 - он под GPL, его вообше нельзя использовать в проприетарном ПО.
		# GPL - это copyleft лицензия, обязывающая распространаять ПО его использующее под такой-же лицензией,
		# и обязывает опубликовать весь код в открытый доступ.
		# Конкретно CKEditor (4 & 5) имеет вторую лицензию для коммерции, но там нужно платить за использование
		# правообладателю: компании CKSource.
		# Так-то только в админке используем и почти всем до этого нет никакого дела, но фактически это
		# нарушение лицензии и закона соответственно. CKEditor НЕЛЬЗЯ использовать в проприетарном ПО на
		# бесплатных основаниях, "либо платите, либо открывайте исходный код" - вот их условия.
		# А вот TinyMCE 6.0 под MIT, и его можно легально использовать почти как угодно, включая проприетарное ПО.
		# Но TinyMCE версии 7 и выше - уже под GPLv2, их нельзя.

		# UPD: Потестил на дебаг странице (рендеринг) - всё работает как по маслу, внутри конечно грязь из тегов,
		# но это почти ни на что не влияет, жить можно. Главное - помечать for & if как div стиль текста, так как
		# p по умолчанию идёт с отступами, которые как раз всё и "ломают" (большие отступы между строками)

	class Meta:
		verbose_name = 'Страница'
		verbose_name_plural = 'Страницы'

	def clean(self):
		from core.views import GenericPageView
		self_url = self.get_absolute_url()

		# INFO: Должно быть настроено
		try: match = resolve(self_url)
		except Resolver404: raise Exception(
			'Вы забыли добавить GenericPageView в urlpatterns, либо он настроен так, '
			'что НЕ перехватывает все входящие запросы (path("<path:url_path>", ...)).'
		)


		def resolved_by_generic_view(match: ResolverMatch):
			if not hasattr(match.func, 'view_class'): # FB-View case
				return False
			return match.func.view_class is GenericPageView

		if not self.is_generic_page and resolved_by_generic_view(match):
			raise ValidationError({
				'url_path':
					f'Страница по URL "{self.get_absolute_url()}" не найдена'
					' (логика работы при is_generic_page:❌).'
			})

		if self.is_generic_page:
			if not self.template_name:
				raise ValidationError({
					'template_name': 'template_name не может быть пустым при is_generic_page:✅.'
				})

			# Указано is_generic_page:✅, но также есть перекрывающий (конфликтующий)
			# view по такому же пути
			if not resolved_by_generic_view(match):
				view_f = match.func
				raise ValidationError({
					'url_path': (
						f'Страница по URL "{self.get_absolute_url()}" перекрывается ' +
						f'{'Class-Based' if hasattr(view_f, 'view_class') else 'Func-Based'} view ' +
						(f'(url name = {match.view_name})' if match.url_name else '') +
						' (логика работы при is_generic_page:✅).'
					)
				})


	def get_absolute_url(self):
		return f"/{self.url_path}"

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

# TODO: Перевести на встроенное кэширование с инвалидацией, вместо самописного
# https://chat.deepseek.com/a/chat/s/a35b0278-5152-4e94-87a1-491bbc2f811c
class TelegramSendingChannel(models.Model):
	class Specialization(models.TextChoices):
		NEW_REQUEST_NOTIFICATIONS = (
			'new_request_notifications', 'Уведомления о новых заявках')
		LOGS = ('logs', 'Логи')
		# Добавлять новые специализации тут

	_cached_instances: dict[Specialization, Self | None] = {}
	_cache_lock: Lock = Lock()

	# Ядерный костылище, нарушает SRP
	_tg_token_validation_warning_message: str | None = None
	# Используется в админке

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
		verbose_name_plural = 'Каналы отправки сообщений в Telegram'

	def __str__(self):
		return self.get_specialization_display()

	@classmethod
	def _invalidate_cache(cls, specialization: Specialization):
		with cls._cache_lock:
			if specialization in cls._cached_instances:
				cls._cached_instances.pop(specialization)

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

	@classmethod
	def get_by_specialization(cls, specialization: Specialization) -> Self | None:
		"""Используется кэширование"""
		with cls._cache_lock:
			if specialization in cls._cached_instances:
				return cls._cached_instances[specialization]

		instance = None
		try: instance = cls.objects.get(specialization = specialization)
		except cls.DoesNotExist: pass

		with cls._cache_lock:
			cls._cached_instances[specialization] = instance

		return instance

	# NOTE: может лучше get_token()?
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

		# else потому, что это метод общей валидации модели, а не только поля с токеном.
		else:
			# Сейчас я считаю эту проверку неоправданной так как
			# её реализацая заняла слишком много времени и она всё равно не
			# даёт гарантии, что токен существует.

			# TODO: Убрать проверку, она нарушает SRP и не имеет смысла
			try:
				response = requests.get(
					url = self._get_api_url('getMe'),
					timeout = TELEGRAM_SENDING.CHECK_TOKEN_EXSISTS_TIMEOUT
				)

				if not response.json()['ok']:
					raise ValidationError(
						'Указанный в ENV-переменной токен не существует в Телеграмм-системе.'
					)
			except requests.RequestException as ex:
				_logger.error(f'Ошибка при попытке выяснить существует ли токен в Телеграмм-системе: {ex}')

				self._tg_token_validation_warning_message = (
					'Не удалось выяснить, существует ли токен указанный для канала '
					f'"{self}" в Телеграмм-системе, '
					'есть риск ошибок в будущем, если был задан некорректный токен.'
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
