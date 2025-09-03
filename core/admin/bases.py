from django.utils.safestring 	import mark_safe
from django.core.exceptions 	import ImproperlyConfigured
from django.contrib 			import admin

from core.models.bases import BaseRenderableModel


class BaseRenderableModelAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ['name']}
	list_display = ('__str__', 'absolute_url')

	def absolute_url(self, obj: BaseRenderableModel):
		try:
			link = obj.get_absolute_url()
			return mark_safe(f'<a href="{link}">{link}</a>')
		except ImproperlyConfigured:
			return mark_safe('<span style="color: red;">Не настроено</span>')
	absolute_url.short_description = 'URL Путь'
