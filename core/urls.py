from django.urls 	import path
from core 			import views


urlpatterns = [
	path('favicon.ico', views.FaviconView.as_view()),

	# Должно быть в САМОМ низу.
	path('', views.GenericPageDetailsView.as_view(), kwargs={'url_path': ''}),
	path('<path:url_path>', views.GenericPageDetailsView.as_view())
]
