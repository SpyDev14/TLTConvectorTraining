from dataclasses 	import asdict
from functools 		import cached_property
from typing 		import Self
from os 			import getenv

from django.db 			import models

from ckeditor.fields	import RichTextField
import requests

from shared.telegram.structures import Message
from shared.models.validators 	import TemplateWithThisNameExists, EnvVariableName


class Page(models.Model):
	# slug = models.CharField("Slug", help_text="Уникальный ID страницы")
	page_name = models.CharField("Название страницы", max_length = 64)
	h1 = models.CharField('H1 Заголовок', max_length = 128)
	template_name = models.CharField('Название django-темплейта',
		validators=[TemplateWithThisNameExists.validator],
		help_text = 'Путь к файлу .html')
	html_title = models.CharField("HTML Title", max_length = 32)
	description = models.CharField("HTML Description", max_length = 32)
	ceo_content = RichTextField("CEO контент", blank = True,
		help_text = "Основное наполнение страницы")

	class Meta:
		verbose_name = "Страница"
		verbose_name_plural = "Страницы"

	def __str__(self):
		return self.page_name


class TelegramSendingChannel(models.Model):
	class TokenEnvNotExistsError(RuntimeError):
		def __init__(self, bot: 'TelegramSendingChannel', *args):
			super().__init__(*args)
			self._bot = bot

		def __str__(self):
			return f"Token ENV variable with name {self._bot.token_env_name} is not exists."

	class Specialization(models.TextChoices):
		NEW_REQUEST_NOTIFICATIONS = (
			'new_request_notifications', 'Уведомления о новых заявках')
		LOGS = ('logs', 'Логи')

	token_env_name = models.CharField('ENV-переменная с токеном', validators = [EnvVariableName.validator],
		help_text = 'Название ENV переменной с токеном этого бота.')
	chat_id = models.CharField('ID чата', max_length = 32)
	channel_specialization = models.CharField('Специализация канала', choices = Specialization.choices,
		unique = True)

	def __init_subclass__(cls):
		super().__init_subclass__()
	
		cls._cached_instances: \
			dict['TelegramSendingChannel.Specialization', 'TelegramSendingChannel'] = {}

	@classmethod
	def _invalidate_cache(cls, specialization: Specialization):
		cls._cached_instances.pop(specialization)

	def save(self, force_insert = ..., force_update = ..., using = ..., update_fields = ...):
		self.__class__._invalidate_cache(self.channel_specialization)
		return super().save(force_insert, force_update, using, update_fields)

	@classmethod
	def get_by_specialization(cls, specialization: Specialization) -> Self | None:
		"""Используется кэширование"""
		if specialization in cls._cached_instances:
			return cls._cached_instances[specialization]

		try:
			instance = cls.objects.get(channel_specialization = specialization)
			cls._cached_instances[specialization] = instance
		except cls.DoesNotExist:
			instance = None

		return instance

	@cached_property
	def api_base_url(self):
		"""Возвращает url-строку с подставленным токеном без `/` в конце.
		**НЕ проверяет**, указан ли токен."""
		return f"https://api.telegram.org/bot{self.token}"

	@cached_property
	def token(self):
		return getenv(self.token_env_name)

	@cached_property
	def token_setted(self):
		"""Вернёт `False`, если env-переменной не существует, или была задана пустая строка."""
		return bool(self.token)

	@cached_property
	def token_exists(self):
		"""Делает запрос к Telegram и проверяет, существует ли указанный токен."""
		# FIXME: Добавить обработку ошибок сети
		response = requests.get(
			url = f'{self.api_base_url}/getMe'
		)
		return response.json()['ok']

	def send_message(self, message: Message) -> None:
		if not self.token_setted:
			raise self.TokenEnvNotExistsError(self)
		
		if not self.token_exists:
			raise ValueError("Переданного токена не существует в Телеграмм системе.")

		url = f'{self.api_base_url}/sendMessage'
		requests.post(url, json = asdict(Message))

	# INFO: Можно написать кастомный декоратор, делающий try-функции
	def try_send_message(self, message: Message) -> tuple[bool, Exception | None]:
		try:
			self.send_message(message)
			return (True, None)

		except Exception as ex:
			return (False, ex)
