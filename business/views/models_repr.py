from core.config 	import GENERIC_TEMPLATE
from core.views 	import BaseRenderableDetailView, PageBasedListView
from business 		import models


# MARK: Article
class ArticleListView(PageBasedListView):
	page_slug = 'blog'
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
	page_slug = 'catalog'
	model = models.Category

# MARK: Service
class ServiceListView(PageBasedListView):
	page_slug = 'services'
	model = models.Service

class ServiceDetailView(BaseRenderableDetailView):
	model = models.Service
	template_name = GENERIC_TEMPLATE.MODEL_DETAIL
