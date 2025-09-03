from django.utils.safestring 	import mark_safe
from django.core.exceptions 	import ValidationError
from django.conf 				import settings
from django.db 					import models

from tinymce.models 	import HTMLField
from mptt.models 		import MPTTModel, TreeForeignKey

from core.models.bases import BaseRenderableModel


class Category(MPTTModel, BaseRenderableModel):
	_custom_url_name = 'subcatalog'

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		from business.models import Product

		self.products: models.Manager[Product]
		self.childrens: models.Manager['Category']

	parent = TreeForeignKey('self', models.CASCADE, verbose_name = 'Родительская категория',
		null = True, blank = True,
		related_name = 'childrens')
	is_parent_category = models.BooleanField('Это родительская категория?', default = True,
		help_text = mark_safe(
			'✅: Можно разместить подкатегории, нельзя разместить товары.<br>'
			'❌: Можно разместить товары, нельзя разместить подкатегории.'))
	image = models.ImageField('Изображение', upload_to = settings.IMAGES_ROOT/'categories')
	summary = HTMLField('Краткое описание (summary)', max_length = 1024, blank = True,
		help_text = 'Краткая информация о категории')

	class Meta:
		verbose_name = 'Категория'
		verbose_name_plural = 'Категории'

	class MPTTMeta:
		order_insertion_by = ['name']

	# INFO: НЕ ИСПОЛЬЗУЙТЕ НИГДЕ КРОМЕ АДМИНКИ!!!!
	def __str__(self):
		linked_objects_count: int = (
			self.childrens.count()
			if self.is_parent_category
			else self.products.count()
		)

		# см. ниже
		data = (
			{'ico': '🗂', 'spec': 'подкатегорий'}
			if self.is_parent_category else
			{'ico': '📦', 'spec': 'товаров'}
		)

		return "{ico} | {name} (для {spec}) (🔗{count}{ico})".format(
			name = self.name,
			count = linked_objects_count,
			**data
		)

	def get_absolute_url(self):
		return "/"

	# NOTE: Не вызывается при перемещении через древо
	def clean(self):
		# Не изменение
		if self.pk is None:
			return

		# Запрет изменения типа категории при наличии детей
		if not self.is_parent_category and self.childrens.exists():
			raise ValidationError({'is_parent_category': 'Нельзя изменить тип: есть подкатегории'})

		# Запрет изменения типа категории при наличии товаров
		if self.is_parent_category and self.products.exists():
			raise ValidationError({'is_parent_category': 'Нельзя изменить тип: категория содержит товары'})
