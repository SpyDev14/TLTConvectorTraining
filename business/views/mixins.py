from feedback_requests.forms 	import FeedbackRequestForm
from core.views 				import PageWithFormView

# Раньше был базовый класс, сделал миксином
class FeedbackRequestFormMixin:
	form_class = FeedbackRequestForm
	success_url = '/success/'
