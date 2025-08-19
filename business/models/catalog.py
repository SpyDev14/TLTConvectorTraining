from django.utils.safestring 	import mark_safe
from django.core.exceptions 	import ValidationError
from django.conf 				import settings
from django.db 					import models

from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
	products: models.Manager # Product (circular import)

	name = models.CharField('Название', unique = True, max_length = 32)
	image = models.ImageField('Изображение', upload_to = settings.IMAGES_ROOT/'categories')
	parent = TreeForeignKey(
		'self',
		verbose_name = 'Родительская категория',
		on_delete = models.CASCADE,
		null = True, blank = True,
		related_name = 'childrens'
	)
	childrens: models.Manager['Category']
	is_parent_category = models.BooleanField('Это родительская категория?', default = True,
		help_text = mark_safe(
			'✅: Можно разместить подкатегории, нельзя разместить товары.<br>'
			'❌: Можно разместить товары, нельзя разместить подкатегории.')
	)

	class Meta:
		verbose_name = 'Категория'
		verbose_name_plural = 'Категории'

	class MPTTMeta:
		order_insertion_by = ['name']

	def __str__(self):
		return self.name

	def clean(self):
		# Не изменение
		if self.pk is None:
			return

		# Запрет изменения типа категории при наличии детей
		if not self.is_parent_category and self.childrens.exists():
			raise ValidationError('Нельзя изменить тип: есть подкатегории')

		# Запрет изменения типа категории при наличии товаров
		if self.is_parent_category and self.products.exists():
			raise ValidationError("Нельзя изменить тип: категория содержит товары")
