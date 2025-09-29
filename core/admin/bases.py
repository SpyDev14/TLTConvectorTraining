from django.utils.safestring 	import mark_safe
from django.core.exceptions 	import ImproperlyConfigured
from django.contrib 			import admin

from core.models.bases import BaseRenderableModel


class BaseRenderableModelAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug': ['name']}
	list_display = ('__str__', 'view_on_site_link')

	# Название "view_on_site" ломает кнопку "Смотреть на сайте" в админке
	def view_on_site_link(self, obj: BaseRenderableModel):
		try:
			return mark_safe(
				f'<a href="{obj.get_absolute_url()}" '
				"style=\"font-family: 'Cascadia Code', 'JetBrains Mono', consolas;\">"
				'[Перейти]</a>'
			)
		except ImproperlyConfigured:
			return mark_safe('<span style="color: red;">Не настроено</span>')
	view_on_site_link.short_description = 'Ссылка'
