from pathlib import Path

from django.conf 	import settings
from django.db 		import models

from ckeditor.fields import RichTextField

from core.models.bases import BaseRenderableModel


_SERVICE_IMGS_PATH: Path = settings.IMAGES_ROOT / 'services'
class Service(BaseRenderableModel):
	examples: models.Manager['PerformedServiceExample']

	image = models.ImageField('Изображение', upload_to = _SERVICE_IMGS_PATH)
	description = RichTextField('Описание')
	summary = models.TextField('Краткое описание', max_length = 768,
		help_text = "Отображается на странице всех услуг в списке услуг")

	class Meta:
		verbose_name = 'Услуга'
		verbose_name_plural = 'Услуги'


class PerformedServiceExample(models.Model):
	service = models.ForeignKey(Service, models.CASCADE, 'examples', verbose_name = 'Услуга')
	image = models.ImageField('Изображение', upload_to = _SERVICE_IMGS_PATH / 'examples')

	class Meta:
		verbose_name = 'Пример выполненой услуги'
		verbose_name_plural = 'Примеры выполненой услуги'
