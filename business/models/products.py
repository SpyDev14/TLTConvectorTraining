from pathlib import Path

from django.conf 	import settings
from django.db 		import models

from ckeditor.fields import RichTextField

from business.models import Category


_PRODUCTS_IMGS_BASE_PATH: Path = settings.IMAGES_ROOT / 'products'
class Product(models.Model):
	photos: models.Manager['ProductPhoto']
	characteristics: models.Manager['ProductCharacteristic']
	additional_elements: models.Manager['ProductAdditionalElements']

	name = models.CharField('Название', max_length = 64)
	category = models.ForeignKey(Category, models.CASCADE, related_name = 'products',
		verbose_name = 'Категория')
	description = RichTextField('Описание')
	blueprint_image = models.ImageField('Чертёж', blank = True, upload_to = _PRODUCTS_IMGS_BASE_PATH / 'blueprints')
	sub_models_table = RichTextField('Таблица под-моделей товара', blank = True,
		help_text = 'Создайте и заполните HTML таблицу с под-моделями товара')


class ProductPhoto(models.Model):
	product = models.ForeignKey(Product, models.CASCADE, related_name = 'photos',
		verbose_name = 'Продукт')
	image = models.ImageField(upload_to = _PRODUCTS_IMGS_BASE_PATH / 'photos')


class ProductCharacteristicType(models.Model):
	name = models.CharField('Тип характеристики', max_length = 24)
	unit_of_measurement = models.CharField('Единицы измерения', max_length = 12, blank = True,
		help_text = 'Например: "мм", "лет", "МПа", "C°" и так далее.')

	class Meta:
		verbose_name = 'Тип характеристики'
		verbose_name = 'Типы характеристик'

	def __str__(self):
		return self.name + f", {self.unit_of_measurement}" if self.unit_of_measurement else ''


class ProductCharacteristic(models.Model):
	product = models.ForeignKey(Product, models.CASCADE, related_name = 'characteristics',
		verbose_name = 'Продукт')
	type = models.ForeignKey(ProductCharacteristicType, models.CASCADE, verbose_name = 'Тип')
	value = models.CharField('Значение', max_length = 24)

	class Meta:
		unique_together = [('product', 'type')]

	def __str__(self):
		return f"{self.type} — {self.value}"


class ProductAdditionalElements(models.Model):
	product = models.ForeignKey(Product, models.CASCADE, related_name = 'additional_elements')
	name = models.CharField('Наименование', max_length = 512)

	def __str__(self):
		return self.name
