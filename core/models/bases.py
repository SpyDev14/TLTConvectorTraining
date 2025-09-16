from django.core.exceptions 			import ImproperlyConfigured
from django.urls 						import reverse, NoReverseMatch
from django.db 							import models

from shared.seo.og 						import OgType


class BaseRenderableModel(models.Model):
	# см. get_absolute_url()
	# Под редкое переопределение в подклассах
	_custom_url_name: str | None = None
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


	class Meta:
		abstract = True

	def __str__(self):
		return self.name

	# Необходимо указать в дочернем классе, но можно оставить пустым
	# NOTE: Может сделать по умолчанию website? Как лучше?????????
	og_type: OgType | None = None

	@property
	def h1(self):
		return self.h1_override or self.name

	@property
	def html_title(self):
		return self.html_title_override or self.name

	def get_absolute_url(self) -> str:
		default_url_name = f'{self._meta.model_name}-detail'
		url_name = self._custom_url_name or default_url_name

		# raise NotImplementedError('Должно быть реализованно в дочернем классе!')
		try:
			return reverse(url_name, kwargs = {self._url_kwarg_name: self.slug})
		except NoReverseMatch:
			raise ImproperlyConfigured(
				'Вы не настроили get_absolute_url()! Настройте, либо переопределите базовый метод.'
			)


	def get_admin_url(self):
		return f'/admin/{self._meta.app_label}/{self._meta.model_name}/{self.pk}/change/'
