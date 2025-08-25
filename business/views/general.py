from django.views.generic.edit 	import ModelFormMixin, ProcessFormView, CreateView

from feedback_requests.forms 	import FeedbackRequestForm
from core.views 				import FormPageView


class HomePageView(FormPageView):
	page_slug = 'home'
	form_class = FeedbackRequestForm
	success_url = 'success/'
