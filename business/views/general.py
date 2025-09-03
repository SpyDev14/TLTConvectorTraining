from core.views.bases 	import BaseRenderableDetailView, PageBasedListView, RenderableModelBasedListView
from core.config 		import GENERIC_TEMPLATE
from business 			import models


# MARK: Article
class ArticleListView(PageBasedListView):
	renderable_slug = 'blog'
	queryset = models.Article.objects.ceo_ordered()

class ArticleDetailView(BaseRenderableDetailView):
	model = models.Article
	template_name = GENERIC_TEMPLATE.MODEL_DETAIL


# MARK: Product & Category details
class ProductDetailView(BaseRenderableDetailView):
	object: models.Product
	model = models.Product

	# def get_queryset(self):
	# 	return super().get_queryset().select_related(
	# 		'photos', 'characteristics', 'additional_elements')

	def get_context_data(self, **kwargs):
		return super().get_context_data(
			photos = self.object.photos.all(),
			characteristics = self.object.characteristics.all(),
			additional_elements = self.object.additional_elements.all()
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
			return self.renderable_object.products.all()

class CatalogPageView(PageBasedListView):
	renderable_slug = 'catalog'
	queryset = models.Category.objects.filter(parent = None)
	template_name = GENERIC_TEMPLATE.MODEL_LIST

# MARK: Service
class ServiceListView(PageBasedListView):
	renderable_slug = 'services'
	model = models.Service
	template_name = GENERIC_TEMPLATE.MODEL_LIST

class ServiceDetailView(BaseRenderableDetailView):
	model = models.Service
	template_name = GENERIC_TEMPLATE.MODEL_DETAIL
