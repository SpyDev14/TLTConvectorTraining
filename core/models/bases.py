from django.db import models

from shared.reflection import typename


class BaseRenderableModel(models.Model):
	name = models.CharField('Название', max_length = 64,
		help_text = 'Указывайте человеко-читаемый текст. По умолчанию также '
		'используется для HTML Title и H1.')
	# slug тут не совсем к месту т.к это про получение объекта на основе запроса,
	# но опустим этот момент.
	slug = models.SlugField(max_length = 128, unique = True)

	# При List нам эти поля будут не нужны, но это малая плата за простоту системы
	html_title_override = models.CharField('HTML Title (переопределение)', max_length = 128, blank = True,
		help_text = 'По умолчанию для HTML Title используется Name.')
	html_description = models.CharField('HTML Description', blank = True)
	h1_override = models.CharField('H1 Заголовок (переопределение)', max_length = 127, blank = True,
		help_text = 'По умолчанию для H1 используется Name. ')

	class Meta:
		abstract = True

	def __str__(self):
		return self.name

	@property
	def html_title(self):
		return self.html_title_override or self.name

	@property
	def h1(self):
		return self.h1_override or self.name

	def get_absolute_url(self) -> str:
		raise NotImplementedError('Должно быть реализованно в дочернем классе!')

	def get_admin_url(self):
		return f'/admin/{self._meta.app_label}/{typename(self).lower()}/{self.pk}/change/'
