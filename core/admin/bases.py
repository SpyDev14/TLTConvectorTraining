from logging import getLogger

from django.utils.safestring 	import mark_safe
from django.core.exceptions 	import ImproperlyConfigured
from django.contrib 			import admin

from mptt.admin import DraggableMPTTAdmin

from core.models.bases 	import BaseRenderableModel
from shared 			import typename

_logger = getLogger(__name__)

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
		except Exception as ex:
			_logger.error(f'Ошибка {typename(ex)}: {ex}', ex)
			font_family = "'JetBrains Mono', 'Cascadia Code', 'consolas'"
			return mark_safe(
				'<details style="color: red; max-width: 10vw;">'
					f'<summary>Ошибка</summary>'
					f'<div style="font-weight: 500; font-family: {font_family};">{typename(ex)}</div>'
					'<div style="background-color: red; height: 1px;"></div>'
					f'<div style="padding-left: 0.25rem; font-family: consolas">{ex}</div>'
				f'</details>'
			)
	view_on_site_link.short_description = 'Ссылка'

# Было нужно, но раз уже сделал, зачем удалять?
class RenderableMPTTAdmin(DraggableMPTTAdmin, BaseRenderableModelAdmin):
	append_to_list_display = ('view_on_site_link',)

	@property
	def list_display(self):
		return DraggableMPTTAdmin.list_display + self.append_to_list_display
