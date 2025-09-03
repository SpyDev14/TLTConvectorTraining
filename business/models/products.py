from pathlib import Path

from django.core.exceptions import ValidationError
from django.conf 			import settings
from django.db 				import models

from tinymce.models 	import HTMLField

from core.models.bases 			import BaseRenderableModel
from business.models.category 	import Category


_PRODUCTS_IMGS_BASE_PATH: Path = settings.IMAGES_ROOT / 'products'
class Product(BaseRenderableModel):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.photos: models.Manager['ProductPhoto']
		self.characteristics: models.Manager['ProductCharacteristic']
		self.additional_elements: models.Manager['ProductAdditionalElements']

	category = models.ForeignKey(Category, models.CASCADE, related_name = 'products',
		verbose_name = 'Категория')
	description = HTMLField('Описание')
	blueprint_image = models.ImageField('Чертёж', blank = True, upload_to = _PRODUCTS_IMGS_BASE_PATH / 'blueprints')
	additional_elements_description = HTMLField('Описание в разделе дополнительных элементов и комплектации',
		blank = True)
	sub_models_table = HTMLField('Таблица под-моделей товара', blank = True,
		help_text = 'Создайте и заполните HTML таблицу с под-моделями товара')
	in_stock = models.BooleanField('В наличии', default = True)


	class Meta:
		verbose_name = 'Товар'
		verbose_name_plural = 'Товары'

	def __str__(self):
		return f'{self.category.name}/{self.name}'

	def clean(self):
		if self.category:
			if self.category.is_parent_category:
				raise ValidationError({"category":"Продукт нельзя прикрепить к категории для категорий"})


class ProductPhoto(models.Model):
	product = models.ForeignKey(Product, models.CASCADE, related_name = 'photos',
		verbose_name = 'Продукт')
	image = models.ImageField('Изображение', upload_to = _PRODUCTS_IMGS_BASE_PATH / 'photos')

	class Meta:
		verbose_name = 'Изображение товара'
		verbose_name_plural = 'Изображения товара'

	def __str__(self):
		return f"Image №{self.pk} for \"{self.product}\""


class ProductCharacteristicType(models.Model):
	name = models.CharField('Название типа характеристики', max_length = 64)
	unit_of_measurement = models.CharField('Единицы измерения', max_length = 24, blank = True,
		help_text = 'Например: "мм", "лет", "МПа", "C°" и так далее. Можно оставить пустым.')

	class Meta:
		unique_together = [('name', 'unit_of_measurement')]
		verbose_name = 'Тип характеристики'
		verbose_name_plural = 'Типы характеристик'
		ordering = ['name', 'unit_of_measurement']

	def __str__(self):
		return self.name + (f", {self.unit_of_measurement}" if self.unit_of_measurement else '')


class ProductCharacteristic(models.Model):
	product = models.ForeignKey(Product, models.CASCADE, related_name = 'characteristics',
		verbose_name = 'Продукт')
	type = models.ForeignKey(ProductCharacteristicType, models.CASCADE, verbose_name = 'Тип')
	value = models.CharField('Значение', max_length = 24)

	class Meta:
		unique_together = [('product', 'type')]
		verbose_name = 'Характеристика товара'
		verbose_name_plural = 'Характеристики товара'

	def __str__(self):
		return f"{self.type} — {self.value}"


class ProductAdditionalElements(models.Model):
	product = models.ForeignKey(Product, models.CASCADE, related_name = 'additional_elements')
	name = models.CharField('Наименование', max_length = 512)

	class Meta:
		verbose_name = 'Дополнительный элемент товара'
		verbose_name_plural = 'Дополнительные элементы товара'

	def __str__(self):
		return self.name
