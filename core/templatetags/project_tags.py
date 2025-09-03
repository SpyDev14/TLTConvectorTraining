# Эти теги по умолчанию добавляются в каждый темплейт (указано в настройках)

from django.utils.safestring 	import mark_safe
from django.template 			import Template, RequestContext, Library


register = Library()

@register.simple_tag(takes_context = True)
def render_as_template(context: RequestContext, template_string: str):
	"""
	Рендерит строку как шаблон с полным текущим контекстом,
	после чего помечает строку как безопасную и возвращает результат.
	Использование: `{% render model.text_field %}`
	"""

	template = Template(str(template_string))
	return mark_safe(
		template.render(context)
	)

@register.filter
def get_attr(obj, attr_name: str):
	return getattr(obj, attr_name)
