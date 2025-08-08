from django.contrib.admin 	import ModelAdmin, action
from django.utils 			import timezone

from rangefilter.filters import DateRangeFilter

from shared.string_processing.resizing 	import truncate_string
from shared.admin.model_registration 	import AdminModelRegistrator
from shared.admin.exporting 			import make_export_to_excel_action
from feedback_requests.models 					import FeedbackRequest
from feedback_requests.apps 						import RequestsConfig


registrator = AdminModelRegistrator(
	app_name = RequestsConfig.name
)

@registrator.set_for_model(FeedbackRequest)
class FeedbackRequestAdmin(ModelAdmin):
	readonly_fields = ('created_at', )
	actions = [make_export_to_excel_action(
		"Заявки",
		add_date_to_name = True,
		set_ordering = ('created_at')
	)]
	list_display = ('request_from', 'phone_number', 'created_at')
	list_filter = (
		('created_at', DateRangeFilter),
	)
	sortable_by = ('created_at', )
	ordering = ('-created_at', )

	def request_from(self, obj: FeedbackRequest) -> str:
		return obj.requestener_name
	request_from.short_description = 'Заявка от'

registrator.register()
