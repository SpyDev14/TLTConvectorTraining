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
	# Должно быть в САМОМ низу, ловит ВСЕ запросы.
	path('', views.GenericPageView.as_view(), kwargs={'url_path': ''}),
	path('<path:url_path>', views.GenericPageView.as_view())
])
