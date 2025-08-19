from django.urls import path

from feedback_requests.forms 	import FeedbackRequestForm
from core.views 				import FormPageView


urlpatterns = [
	path('', FormPageView.as_view(
			page_slug = 'home',
			form_class = FeedbackRequestForm,
			success_url = 'success/',
		),
	),
]
