from django.db import models

from shared.reflection import typename


class BaseRenderableModel(models.Model):
	name = models.CharField('Название', max_length = 64,
		help_text = 'Указывайте человеко-читаемый текст. По умолчанию также '
		'используется и для формирования HTML Title')
	# slug тут не совсем к месту т.к это про получение объекта на основе запроса,
	# но опустим этот момент.
	slug = models.SlugField(max_length = 128, unique = True)

	# При List нам эти поля будут не нужны, но это малая плата за простоту системы
	html_title_override = models.CharField('HTML Title override', max_length = 128, blank = True,
		help_text = 'По умолчанию для формирования HTML Title используется verbose_name.'
		'Укажите здесь свой title, и он будет использован вместо него.')
	html_description = models.CharField('HTML Description', blank = True)

	class Meta:
		# Добавить в Meta штуку для html_title_list
		abstract = True

	def __str__(self):
		return self.name

	@property
	def html_title(self):
		return self.html_title_override or self.name

	def get_absolute_url(self) -> str:
		raise NotImplementedError('Должно быть реализованно в дочернем классе!')

	def get_admin_url(self):
		return f'/admin/{self._meta.app_label}/{typename(self).lower()}/{self.pk}/change/'
