import logging

from django.contrib.admin import ModelAdmin

from shared.admin.model_registration 	import AdminModelRegistrator
from core.apps 							import CoreConfig

registrator = AdminModelRegistrator(
	app_name = CoreConfig.name,
	logger = logging.getLogger(__name__)
)

registrator.register()
