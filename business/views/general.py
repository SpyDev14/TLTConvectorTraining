from django.shortcuts 			import redirect
from django.http 				import HttpRequest

from feedback_requests.forms 	import FeedbackRequestForm
from core.views 				import FormPageView


class HomePageView(FormPageView):
	page_slug = 'home'
	form_class = FeedbackRequestForm
	success_url = 'success/'
