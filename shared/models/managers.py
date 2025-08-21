from django.db.models.manager import BaseManager
from shared.models import querysets

__all__ = [
	'IndividualizedBulkOperationsManager'
]

class IndividualizedBulkOperationsManager(
		BaseManager.from_queryset(querysets.IndividualizedBulkOperationsQuerySet)):
	"""
	Заменяет массовые операции на индивидуальные операции с каждым
	элементом в QuerySet. Используйте, когда важно, чтобы метод save() & delete()
	был вызван для каждой модели.

	Внимание! Все Bulk операции будут выполнять N SQL запросов, вместо одного!
	"""
	pass
