from django.utils.safestring 	import mark_safe
from django.utils.html 			import escape
from django.template 			import RequestContext, Library

from shared.reflection import typename


register = Library()
register.filter('typename', typename)


@register.simple_tag(takes_context=True)
def current_context(context: RequestContext):
	"""Возвращает весь текущий контекст в виде HTML-структуры"""
	# Писал ИИ, дальше бога нет.

	def format_value(obj, depth=0):
		if depth > 10:  # Защита от глубокой рекурсии
			return mark_safe('<span style="color:red">Too deep recursion</span>')

		if isinstance(obj, dict):
			return format_dict(obj, depth + 1)
		elif isinstance(obj, (list, tuple, set)):
			return format_list(obj, depth + 1)
		else:
			return format_basic_type(obj)

	def format_dict(d, depth):
		items = []
		for k, v in d.items():
			safe_key = escape(str(k))
			items.append(f'''
			<div style="margin-left: {depth * 20}px">
				<strong>{safe_key}:</strong> {format_value(v, depth)}
			</div>''')
		return mark_safe(''.join(items))

	def format_list(seq, depth):
		items = []
		for i, item in enumerate(seq):
			items.append(f'''
			<div style="margin-left: {depth * 20}px">
				<strong>[{i}]:</strong> {format_value(item, depth)}
			</div>''')
		return mark_safe(''.join(items))

	def format_basic_type(obj):
		obj_type = escape(type(obj).__name__)
		obj_repr = escape(repr(obj))

		if len(obj_repr) > 100:
			obj_repr = f'''
			<details style="margin-left: 20px">
				<summary><strong>view repr</strong> (repr is too long)</summary>
				{obj_repr}
			</details>
			'''

		return mark_safe(f'''
		<span style="color:gray">({obj_type})</span> {obj_repr}
		''')

	context_data = context.flatten()
	return mark_safe(f'''
	<details open style="font-size: 12px; border: 1px solid #ccc; padding: 10px">
		<summary style="cursor: pointer; outline: none">
			<strong>Template Context</strong>
		</summary>
		{format_value(context_data)}
	</details>
	''')
	# <div style="font-size: 0.75rem; border: 1px solid #ccc; padding: 10px">
	# 	<strong>Template Context</strong>
	# 	{format_value(context_data)}
	# </div>
