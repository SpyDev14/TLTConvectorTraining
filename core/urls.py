from django.urls 	import path
from core 			import views


urlpatterns = [
	path('favicon.ico', views.Favicon.as_view()),

	# Должно быть в САМОМ низу.
	path('', views.GenericPageView.as_view(), kwargs={'url_path': ''}),
	path('<path:url_path>', views.GenericPageView.as_view())
]
