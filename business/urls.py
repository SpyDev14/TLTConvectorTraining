from django.urls import path

from business import views


urlpatterns = [
	path('', views.HomePageView.as_view(), name = 'home'),
]
