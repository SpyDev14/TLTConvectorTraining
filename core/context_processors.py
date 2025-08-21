# Сделать позже похожую систему, что была в LTP, но с расширенным
# функционалом и с использованием context processors

# Пока-что сделать топорную схему

# Ну или не делать такую систему вовсе, это тоже неплохо работает и
# соблюдает KISS.
from solo.models 			import SingletonModel

from shared.string_processing.cases import camel_to_snake_case
from core.models.singletons 		import *
from core.models.general 			import Page, ExtraContext


SINGLETON_MODELS: set[type[SingletonModel]] = {
	SiteSettings,
	CompanyContacts
}

# Создаёт нагрузку на БД, но я думаю, не такую сильную, так что нормально
def global_data_context_processor(request): return {
	'global': {
		**{
			camel_to_snake_case(model.__name__): model.get_solo()
			for model in SINGLETON_MODELS
		},
		'pages': {
			page.slug: page for page
			in Page.objects.prefetch_related('extra_context_manager').all()
		},
		'extra_context': {
			ctx.key: ctx.value for ctx
			in ExtraContext.objects.filter(page = None)
		},
	},
}
