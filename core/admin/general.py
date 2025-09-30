from django.utils.safestring 	import mark_safe
from django.contrib 			import admin

from shared.string_processing.resizing 	import truncate_string
from shared.admin.model_registration 	import AdminModelRegistrator
from core.admin.bases 					import BaseRenderableModelAdmin
from core.config 						import GENERIC_TEMPLATE
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
	list_display = ('page', 'slug', 'view_on_site_link', 'page_template_name', 'is_generic_page',)
	inlines = [ExtraContextInline]
	prepopulated_fields = {}
	ordering = ('name',)

	def page(self, obj):
		return str(obj)
	page.short_description = 'Страница'

	def page_template_name(self, obj: models.Page):
		if tname := obj.template_name:
			return tname

		return (
			mark_safe(f'<span title="{GENERIC_TEMPLATE.PAGE}">По умолчанию</span>')
			if obj.is_generic_page else
			mark_safe('<span style="color: grey;">(не generic страница)</span>')
		)
	page_template_name.short_description = models.Page._meta.get_field('template_name').verbose_name


@registrator.set_for_model(models.TelegramSendingChannel)
class TelegramSendingChannelAdmin(admin.ModelAdmin):
	actions = None

	def has_add_permission(self, request):
		count_of_specializations = len(models.TelegramSendingChannel.Specialization)
		count_of_channels = models.TelegramSendingChannel.objects.count()
		# (специализация uniqe = True, blank = False)
		return count_of_channels < count_of_specializations

registrator.register()
