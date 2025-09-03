from feedback_requests.forms 	import FeedbackRequestForm

# Раньше был базовый класс, сделал миксином
class FeedbackRequestFormMixin:
	form_class = FeedbackRequestForm
	success_url = '/success/'
