from core.config 	import GENERIC_TEMPLATE
from core.views 	import BaseRenderableDetailView, PageBasedListView
from business 		import models


# MARK: Article
class ArticleListView(PageBasedListView):
	renderable_slug = 'blog'
	queryset = models.Article.objects.ceo_ordered()

class ArticleDetailView(BaseRenderableDetailView):
	model = models.Article
	template_name = GENERIC_TEMPLATE.MODEL_DETAIL


# MARK: Product & Category
class ProductDetailView(BaseRenderableDetailView):
	model = models.Product
	template_name = GENERIC_TEMPLATE.MODEL_DETAIL

class CategoryDetailView(BaseRenderableDetailView):
	model = models.Category
	template_name = GENERIC_TEMPLATE.MODEL_DETAIL

class CatalogPageView(PageBasedListView):
	renderable_slug = 'catalog'
	model = models.Category
	template_name = GENERIC_TEMPLATE.MODEL_LIST


# MARK: Service
class ServiceListView(PageBasedListView):
	renderable_slug = 'services'
	model = models.Service
	template_name = GENERIC_TEMPLATE.MODEL_LIST

class ServiceDetailView(BaseRenderableDetailView):
	model = models.Service
	template_name = GENERIC_TEMPLATE.MODEL_DETAIL
