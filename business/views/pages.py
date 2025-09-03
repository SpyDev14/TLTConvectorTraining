from core.views.bases import PageWithFormView

from business.views.mixins 	import FeedbackRequestFormMixin
from business 				import models


class HomePageView(FeedbackRequestFormMixin, PageWithFormView):
	template_name = 'business/home.html'
	page_slug = 'home'

	def get_context_data(self, **kwargs):
		context: dict = super().get_context_data(**kwargs)
		context.update({
			'last_articles': models.Article.objects.ceo_ordered()[:2]
		})
		return context


class AboutUsPageView(FeedbackRequestFormMixin, PageWithFormView):
	template_name = 'business/about_us.html'
	page_slug = 'about-us'
