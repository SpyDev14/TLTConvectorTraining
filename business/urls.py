from django.urls import path

from business import views


urlpatterns = [
	path('', views.HomePageView.as_view(), name = 'home'),
	path('about-us/', views.AboutUsPageView.as_view(), name = 'about-us'),
	path('catalog/', views.CatalogPageView.as_view(), name = 'catalog'),

	# Models
	path('products/<slug:slug>/', views.ProductDetailView.as_view(), name = 'product-detail'),
	path('catalog/<slug:slug>/', views.CategoryDetailView.as_view(), name = 'subcatalog'),

	path('blog/', views.ArticleListView.as_view(), name = 'article-list'),
	path('blog/<slug:slug>/', views.ArticleDetailView.as_view(), name = 'article-detail'),

	path('services/', views.ServiceListView.as_view(), name = 'service-list'),
	path('services/<slug:slug>/', views.ServiceDetailView.as_view(), name = 'service-detail'),
]
