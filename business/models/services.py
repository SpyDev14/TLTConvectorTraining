from pathlib import Path

from django.conf 	import settings
from django.db 		import models

from tinymce.models 	import HTMLField

from core.models.bases import BaseRenderableModel


_SERVICE_IMGS_PATH: Path = settings.IMAGES_ROOT / 'services'
class Service(BaseRenderableModel):
	examples: models.Manager['PerformedServiceExample']
	advantages: models.Manager['ServiceAdvantage']

	image = models.ImageField('Изображение', upload_to = _SERVICE_IMGS_PATH)
	description = HTMLField('Описание')
	summary = HTMLField('Краткое описание', max_length = 768,
		help_text = "Отображается на странице всех услуг в списке услуг")

	class Meta:
		verbose_name = 'Услуга'
		verbose_name_plural = 'Услуги'
		ordering = ['name']


class PerformedServiceExample(models.Model):
	service = models.ForeignKey(Service, models.CASCADE, 'examples', verbose_name = 'Услуга')
	image = models.ImageField('Изображение', upload_to = _SERVICE_IMGS_PATH / 'examples')

	class Meta:
		verbose_name = 'Пример выполненой услуги'
		verbose_name_plural = 'Примеры выполненой услуги'

	def __str__(self):
		return f"Пример выполненной услуги №{self.pk}"


class ServiceAdvantage(models.Model):
	service = models.ForeignKey(Service, models.CASCADE, 'advantages', verbose_name = 'Услуга')
	name = models.CharField('Название', max_length = 32)
	description = HTMLField('Описание')
	image = models.ImageField('Изображение', upload_to = _SERVICE_IMGS_PATH / 'advantages', max_length=200)

	class Meta:
		verbose_name = 'Преимущество услуги'
		verbose_name_plural = 'Преимущества услуги'
		unique_together = [('service', 'name')]

	def __str__(self):
		return f"{self.name}"
