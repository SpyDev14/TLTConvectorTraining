from pathlib import Path

from django.core.exceptions import ValidationError
from django.conf 			import settings
from django.db 				import models

from ckeditor.fields import RichTextField

from core.models.bases 	import BaseRenderableModel
from business.models 	import Category

# В отдельной функции, а не в clean, чтобы сообщение было прикреплено к полю category
_PRODUCTS_IMGS_BASE_PATH: Path = settings.IMAGES_ROOT / 'products'
class Product(BaseRenderableModel):
	photos: models.Manager['ProductPhoto']
	characteristics: models.Manager['ProductCharacteristic']
	additional_elements: models.Manager['ProductAdditionalElements']

	category = models.ForeignKey(Category, models.CASCADE, related_name = 'products',
		verbose_name = 'Категория')
	description = RichTextField('Описание')
	blueprint_image = models.ImageField('Чертёж', blank = True, upload_to = _PRODUCTS_IMGS_BASE_PATH / 'blueprints')
	sub_models_table = RichTextField('Таблица под-моделей товара', blank = True,
		help_text = 'Создайте и заполните HTML таблицу с под-моделями товара')

	class Meta:
		verbose_name = 'Товар'
		verbose_name_plural = 'Товары'

	def __str__(self):
		return f'{self.category.name}/{self.name}'

	def clean(self):
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
	name = models.CharField('Название типа характеристики', max_length = 24)
	unit_of_measurement = models.CharField('Единицы измерения', max_length = 12, blank = True,
		help_text = 'Например: "мм", "лет", "МПа", "C°" и так далее. Можно оставить пустым.')

	class Meta:
		unique_together = [('name', 'unit_of_measurement')]
		verbose_name = 'Тип характеристики'
		verbose_name_plural = 'Типы характеристик'

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
