from feedback_requests.forms 	import FeedbackRequestForm
from core.views 				import PageWithFormView

class PageWithFeedbackRequestFormView(PageWithFormView):
	form_class = FeedbackRequestForm
	success_url = 'success/'
