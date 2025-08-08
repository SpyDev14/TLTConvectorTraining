from pathlib import Path

from django.conf 	import settings
from django.db 		import models

from ckeditor.fields import RichTextField


_SERVICE_IMGS_PATH: Path = settings.IMAGES_ROOT / 'services'
class Service(models.Model):
	examples: models.Manager['PerformedServiceExample']

	name = models.CharField('Название', max_length = 64)
	image = models.ImageField('Изображение', upload_to = _SERVICE_IMGS_PATH)
	description = RichTextField('Описание')

	# TODO: Раскомментировать, если буду добавлять поддержку рендеринга в ceo_content страницы
	# NOTE: Удалить перед проверкой, если так и не добавлю.
	# short_description = models.TextField('Краткое описание услуги', max_length = 768,
	# 	help_text = "Отображается на странице всех услуг в списке услуг")


class PerformedServiceExample(models.Model):
	service = models.ForeignKey(Service, models.CASCADE, 'examples', verbose_name = 'Услуга')
	image = models.ImageField('Изображение', upload_to = _SERVICE_IMGS_PATH / 'examples')
