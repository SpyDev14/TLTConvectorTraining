from django.urls import path

from business import views

# INFO: path names - только для работы ИЗ КОДА!!!
# В темплейтах используйте другие источники: get_absolute_url() от объекта и global объекты
# {% for item in items %}
#     {{ item.get_absolute_url }}
# {% endfor %}
# {{ global.pages.contacts.get_absolute_url }}
# NOTE: Может всё-таки разрешить? Надо подумать.

# Формат name: model_name-type
urlpatterns = [
	path('', views.HomePageView.as_view(), name = 'index'),
	path('about-us/', views.AboutUsPageView.as_view(), name = 'about-us'),

	# Models
	path('catalog/', views.CatalogPageView.as_view(), name = 'catalog'),
	path('catalog/<slug:slug>/', views.CategoryDetailView.as_view(), name = 'subcatalog'),

	path('products/<slug:slug>/', views.ProductDetailView.as_view(), name = 'product-detail'),

	path('blog/', views.ArticleListView.as_view(), name = 'article-list'),
	path('blog/<slug:slug>/', views.ArticleDetailView.as_view(), name = 'article-detail'),

	path('services/', views.ServiceListView.as_view(), name = 'service-list'),
	path('services/<slug:slug>/', views.ServiceDetailView.as_view(), name = 'service-detail'),
]
