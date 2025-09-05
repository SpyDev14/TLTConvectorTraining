from django.conf 	import settings
from django.urls 	import path
from core 			import views


urlpatterns = [
	path('favicon.ico', views.FaviconView.as_view()),
]

if settings.DEBUG:
	urlpatterns.extend([
		path('_debug/', views.DebugPageView.as_view(), kwargs={'url_path': ''}, name = 'debug-repr'),
		path('_debug/<slug:slug>/', views.DebugPageView.as_view(), name = 'debug-repr')
	])


urlpatterns.extend([
	# Должно быть в САМОМ низу, ловит ВСЕ запросы.
	path('', views.GenericPageView.as_view(), kwargs={'url_path': ''}),
	path('<path:url_path>', views.GenericPageView.as_view())
])
