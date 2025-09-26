from typing import Any

from django.core.exceptions 			import ImproperlyConfigured
from django.urls 						import reverse, NoReverseMatch
from django.db 							import models

from shared.seo.og 						import OgType


class BaseRenderableModel(models.Model):
	"""
	Базовая модель для всех моделей, что будут отображаться на своих страницах:
	статьи, товары, категории и так далее. Т.е для всех моделей, у которых есть
	details. Работает совместо со специализированными view, которые вы можете
	найти в папке `core/views/bases/`.

	Содержит в себе базово необходимые поля и поля для SEO.
	"""

	# см. get_absolute_url()
	# Под редкое переопределение в подклассах
	_url_name: str | None = None
	_url_kwarg_name: str = 'slug'

	name = models.CharField('Название', max_length = 64,
		help_text = 'Указывайте человеко-читаемый текст. По умолчанию также '
		'используется для HTML Title и H1.')
	# slug тут не совсем к месту т.к это про получение объекта на основе запроса,
	# но опустим этот момент, это слишком мелкая деталь.
	slug = models.SlugField(max_length = 128, unique = True)
	h1_override = models.CharField('H1 Заголовок (переопределение)', max_length = 127, blank = True,
		help_text = 'По умолчанию для H1 используется Name.')

	html_title_override = models.CharField('HTML Title (переопределение)', max_length = 128, blank = True,
		help_text = 'По умолчанию для HTML Title используется Name.')
	html_description = models.CharField('HTML Description', blank = True)
	last_modified_time = models.DateTimeField(auto_now=True)

	class Meta:
		abstract = True

	def __str__(self):
		return self.name


	# Под переопределение
	# А вот в C# есть "=>" выражения для создания таких аллиасов (вместо return)!
	# И в целом там явные св-ва, жалко в python такого нет. Св-ва тут - это дескрипторы,
	# созданные на основе методов класса (которые тоже являются дескрипторами) через декораторную запись (@)
	# (вот тут снизу мы создаём объект класса property, передав в него метод h1 через @ и заменяем этим
	# объектом исходный метод h1 (из-за @))

	@property
	def h1(self) -> str:
		return self.h1_override or self.name

	@property
	def html_title(self) -> str:
		return self.html_title_override or self.name

	# Необходимо указать в дочернем классе, но можно оставить по умолчанию
	og_type: OgType = OgType.WEBSITE

	@property
	def og_title(self) -> str:
		return self.html_title

	@property
	def og_description(self) -> str | None:
		return self.html_description

	@property
	def og_image_url(self) -> str | None:
		return None

	def _get_microdata(self) -> dict[str, Any]:
		"""Под переопределение, возвращайте здесь нужный объект с данными"""
		raise NotImplementedError('Переопределите этот метод в дочернем классе!')

	def get_full_microdata(self) -> dict[str, Any]:
		"""Возвращает self._get_microdata() с подставленным значением по умолчанию"""
		return {
			'@context': 'https://schema.org',
			**self._get_microdata()
		}

	def get_absolute_url(self) -> str:
		default_url_name = f'{self._meta.model_name}-detail'
		url_name = self._url_name or default_url_name

		try:
			return reverse(url_name, kwargs = {self._url_kwarg_name: self.slug})
		except NoReverseMatch:
			raise ImproperlyConfigured(
				'Вы не настроили get_absolute_url()! Настройте, либо переопределите базовый метод.'
			)

	def get_admin_url(self):
		return f'/admin/{self._meta.app_label}/{self._meta.model_name}/{self.pk}/change/'

	@classmethod
	def get_sitemap_queryset(cls):
		return cls.objects.all()
