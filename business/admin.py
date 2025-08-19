from django.contrib import admin

from shared.admin.model_registration 	import AdminModelRegistrator
from business.apps 						import BusinessConfig
from business 							import models

class _TabularInline(admin.TabularInline):
	can_delete = True
	extra = 0

class _StackedInline(admin.StackedInline):
	can_delete = True
	extra = 0


registrator = AdminModelRegistrator(
	app_name = BusinessConfig.name
)

registrator.exclude_model(models.ProductCharacteristic)
class ProductCharacteristicsInline(_TabularInline):
	model = models.ProductCharacteristic

registrator.exclude_model(models.ProductPhoto)
class ProductPhotoInline(_TabularInline):
	model = models.ProductPhoto

registrator.exclude_model(models.ProductAdditionalElements)
class ProductAdditionalElementsInline(_TabularInline):
	model = models.ProductAdditionalElements

@registrator.set_for_model(models.Product)
class ProductModel(admin.ModelAdmin):
	inlines = [
		ProductPhotoInline,
		ProductCharacteristicsInline,
		ProductAdditionalElementsInline,
	]


registrator.register()
