from typing import Any
from abc import ABC, abstractmethod

from django.template.response 	import TemplateResponse
from django.views 				import View

from shared.string_processing.cases import camel_to_snake_case
from shared.reflection 				import typename
from core.models 					import Page


class BasePageView(ABC, View):
	def get_additional_context(self) -> dict[str, Any]:
		"""Под переопределение"""
		return {}

	def get_context(self, *, page: Page, **kwargs) -> dict[str, Any]:
		context = {}
		context.update(self.get_additional_context())
		context.update(kwargs)

		# Всегда передаём текущую страницу как page в контекст,
		# не позволяем переопределять.
		context.update({
			# <type Page> -> "Page" -> "page"
			camel_to_snake_case(typename(Page)): page,
			# В случае чего, в шаблонах, название можно будет заменить через regex замену
			# ({[{%][\w\s]*)page([\w\s.]*[%}]}) -> $1new_name$2 (или как-то так, не помню как группа вставляется)
			# Название всегда должно быть актуальным, иначе верстальщикам придётся держать лишную
			# информацию в голове.
			'debug_info': {
				'view': self.__class__.__name__
			},
		})
		return context

	@abstractmethod
	def get_page_object(self) -> Page:
		pass

	def render_to_response(self, page: Page, context: dict[str, Any], *, status: int = 200):
		return TemplateResponse(self.request, page.template_name, context, status = status)

	def get(self, *args, **kwargs):
		page = self.get_page_object()
		context = self.get_context(page = page)
		return self.render_to_response(page, context)
