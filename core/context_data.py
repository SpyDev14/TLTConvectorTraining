# Сделать позже похожую систему, что была в LTP, но с расширенным
# функционалом и с использованием context processors

# Пока-что сделать топорную схему

from core.models.singletons import *
from solo.models 			import SingletonModel

from shared.string_processing.cases import camel_to_snake_case


SINGLETON_MODELS: set[SingletonModel] = {
	SiteSettings,
	CompanyContacts
}


def global_data_context_processor(request): return {
	'global': {
		**{
			camel_to_snake_case(model.__name__): model.get_solo()
			for model in SINGLETON_MODELS
		},
	}
}

