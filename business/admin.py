from django.contrib import admin

from mptt.admin import MPTTModelAdmin

from shared.admin.model_registration 	import AdminModelRegistrator
from core.admin.bases 					import BaseRenderableModelAdmin
from business.apps 						import BusinessConfig
from business 							import models


registrator = AdminModelRegistrator(
	app_name = BusinessConfig.name
)

@registrator.set_for_model(models.Category)
class CategoryAdmin(BaseRenderableModelAdmin, MPTTModelAdmin):
	pass

# MARK: Product
registrator.exclude_model(models.ProductCharacteristic)
class ProductCharacteristicsInline(admin.TabularInline):
	model = models.ProductCharacteristic
	classes = ('collapse',)
	extra = 4

registrator.exclude_model(models.ProductPhoto)
class ProductPhotoInline(admin.TabularInline):
	model = models.ProductPhoto
	classes = ('collapse',)
	extra = 2

registrator.exclude_model(models.ProductAdditionalElements)
class ProductAdditionalElementsInline(admin.TabularInline):
	model = models.ProductAdditionalElements
	classes = ('collapse',)
	extra = 0

@registrator.set_for_model(models.Product)
class ProductAdmin(BaseRenderableModelAdmin):
	inlines = [
		ProductPhotoInline,
		ProductCharacteristicsInline,
		ProductAdditionalElementsInline,
	]


# MARK: Service
registrator.exclude_model(models.PerformedServiceExample)
class PerformedServiceExampleInline(admin.TabularInline):
	model = models.PerformedServiceExample
	classes = ('collapse',)
	extra = 1

registrator.exclude_model(models.ServiceAdvantage)
class ServiceAdvantageInline(admin.StackedInline):
	model = models.ServiceAdvantage
	classes = ('collapse',)

@registrator.set_for_model(models.Service)
class ServiceAdmin(BaseRenderableModelAdmin):
	inlines = [PerformedServiceExampleInline, ServiceAdvantageInline]

registrator.register()
