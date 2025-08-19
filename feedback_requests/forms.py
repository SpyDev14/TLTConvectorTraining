from django.forms import ModelForm
from .models import FeedbackRequest


class FeedbackRequestForm(ModelForm):
	class Meta:
		model = FeedbackRequest
		fields = '__all__'
