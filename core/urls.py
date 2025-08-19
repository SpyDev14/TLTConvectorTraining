from django.urls 	import path
from core 			import views


urlpatterns = [
	# Должно быть в САМОМ низу.
	path('', views.GenericPageView.as_view(), kwargs={'url_path': ''}),
	path('<path:url_path>', views.GenericPageView.as_view())
]
