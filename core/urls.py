from django.contrib.sitemaps.views 	import sitemap
from django.conf 					import settings
from django.urls 					import path

from core.sitemaps 	import get_base_renderables_sitemaps
from core 			import views

_sitemaps = {
	**get_base_renderables_sitemaps(),
}

urlpatterns = [
	path('favicon.ico', views.FaviconView.as_view()),
	path('robots.txt', views.RobotsView.as_view()),
	path('sitemap.xml', sitemap, kwargs={'sitemaps': _sitemaps})
]

if settings.DEBUG:
	urlpatterns.extend([
		path('_debug/<slug:slug>/', views.DebugPageView.as_view(), name = 'debug-repr')
	])


urlpatterns.extend([
	# Лучше ставить в самом низу, ловит запросы по url первого уровня.
	path('<slug:slug>/', views.GenericPageView.as_view())
])
