from django.contrib import admin, messages

from shared.string_processing.resizing 	import truncate_string
from shared.admin.model_registration 	import AdminModelRegistrator
from core.admin.bases 					import BaseRenderableModelAdmin
from core.apps 							import CoreConfig
from core 								import models

registrator = AdminModelRegistrator(
	app_name = CoreConfig.name,
)

@registrator.set_for_model(models.ExtraContext)
class ExtraContextAdmin(admin.ModelAdmin):
	list_display = ('__str__', 'key', 'source', 'part_of_value', )

	def source(self, obj: models.ExtraContext):
		if obj.page: return 'page'
		return 'global'
	source.short_description = 'Источник'

	def part_of_value(self, obj: models.ExtraContext):
		return truncate_string(obj.value, 100)
	part_of_value.short_description = models.ExtraContext._meta.get_field('value').verbose_name


class ExtraContextInline(admin.TabularInline):
	model = models.ExtraContext
	extra = 0

@registrator.set_for_model(models.Page)
class PageAdmin(BaseRenderableModelAdmin):
	list_display = ('page', 'page_url', 'template_name')
	inlines = [ExtraContextInline]
	prepopulated_fields = {}

	def page(self, obj):
		return str(obj)
	page.short_description = 'Страница'

	def page_url(self, obj: models.Page):
		return obj.get_absolute_url()
	page_url.short_description = models.Page._meta.get_field('url_path').verbose_name


@registrator.set_for_model(models.TelegramSendingChannel)
class TelegramSendingChannelAdmin(admin.ModelAdmin):
	actions = None

	def has_add_permission(self, request):
		count_of_specializations = len(models.TelegramSendingChannel.Specialization)
		count_of_channels = models.TelegramSendingChannel.objects.count()
		# специализация: uniqe = True, blank = False
		return count_of_channels < count_of_specializations

	def save_model(self, request, obj: models.TelegramSendingChannel, form, change):
		if msg := obj._tg_token_validation_warning_message:
			messages.warning(request, msg)

		return super().save_model(request, obj, form, change)

registrator.register()
