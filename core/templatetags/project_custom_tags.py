import logging, json

from django.utils.safestring 	import mark_safe
from django.template 			import Template, RequestContext, Library
from _project_.constants 		import LEVEL_ONLY_LOGGER

from shared.reflection import typename


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

@register.simple_tag(takes_context = True)
def log_context(context: RequestContext):
	"""Выводит в лог весь текущий контекст"""
	logger = logging.getLogger(LEVEL_ONLY_LOGGER)

	def serialize_obj(obj: object):
		data = {
			'type': typename(obj),
			'repr': repr(obj),
		}

		if str(obj) != repr(obj):
			data['str'] = str(obj)

		return data

	context_as_dict = context.flatten()
	logger.debug(
		'Current template context:\n%s' %
		json.dumps(context_as_dict, indent = 4, default = serialize_obj, ensure_ascii = False)
	)

	return ''
