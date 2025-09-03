from abc import ABC, abstractmethod

from django.views import View
from core.models.bases import BaseRenderableModel

class GetRenderableModelStrategy(ABC):
	@abstractmethod
	def get_object(self, view: View) -> BaseRenderableModel:
		pass
