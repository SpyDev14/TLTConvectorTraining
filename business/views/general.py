from core.views.bases 	import BaseRenderableDetailView, PageBasedListView, RenderableModelBasedListView
from business 			import models
from django.db.models 	import Prefetch


# MARK: Article
class ArticleListView(PageBasedListView):
	renderable_slug = 'blog'
	queryset = models.Article.objects.ceo_ordered()

class ArticleDetailView(BaseRenderableDetailView):
	model = models.Article


# MARK: Product & Category details
class ProductDetailView(BaseRenderableDetailView):
	object: models.Product
	queryset = models.Product.objects.prefetch_related(
		Prefetch('photos'),
		Prefetch('additional_elements'),
		Prefetch('characteristics', queryset = models.ProductCharacteristic.objects.select_related('type'))
	).select_related('category')

	def get_context_data(self, **kwargs):
		return super().get_context_data(
			# Kwargs здесь не нужны, это конечный класс
			photos = self.object.photos.all(),
			characteristics = self.object.characteristics.all(),
			additional_elements = self.object.additional_elements.all(),
		)


class CategoryDetailView(RenderableModelBasedListView):
	renderable_model = models.Category
	template_name = 'business/subcatalog.html'

	renderable_object: models.Category

	def get_renderable_queryset(self):
		return models.Category.objects.filter(slug = self.kwargs['slug'])

	def get_queryset(self):
		if self.renderable_object.is_parent_category:
			return self.renderable_object.childrens.all()
		else:
			return self.renderable_object.products.prefetch_related('photos')

class CatalogPageView(PageBasedListView):
	renderable_slug = 'catalog'
	queryset = models.Category.objects.filter(parent = None)


# MARK: Service
class ServiceListView(PageBasedListView):
	renderable_slug = 'services'
	model = models.Service

class ServiceDetailView(BaseRenderableDetailView):
	queryset = models.Service.objects.prefetch_related('examples', 'advantages')
	object: models.Service

	def get_context_data(self, **kwargs):
		return super().get_context_data(
			advantages = self.object.advantages.all(),
			examples = self.object.examples.all()
		)
