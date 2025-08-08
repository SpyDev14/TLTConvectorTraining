from django.contrib import admin

from shared.admin.model_registration 	import AdminModelRegistrator
from business.apps 						import BusinessConfig

registrator = AdminModelRegistrator(
	app_name = BusinessConfig.name
)

registrator.register()
