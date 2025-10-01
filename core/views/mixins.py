from core.models.bases import BaseRenderableModel


class PageInfoMixin:
	"""
	Добавляет page_info в контекст.
	Обычно, это просто дублирует объект в контекстный ключ page_info.
	Обращайтесь к данным о странице через page_info, а не через сам объект!

	Требует:
	- Этот класс имеет реализацию get_context_data
	"""
	def get_page_info(self) -> BaseRenderableModel:
		raise NotImplementedError()

	def get_context_data(self, **kwargs):
		kwargs.update({
			'page_info': self.get_page_info()
		})
		return super().get_context_data(**kwargs)
