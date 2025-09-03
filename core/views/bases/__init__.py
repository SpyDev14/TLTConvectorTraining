"""
Модуль с базовыми View для наследования.
Все эти View здесь потому, что не предполагается, что они
будут использоваться в urlpatterns напрямую.
"""

from .list import (
	RenderableModelBasedListView,
	PageBasedListView
)
from .details import (
	BaseRenderableDetailView,
	BasePageView,
	ConcretePageView,
	PageWithFormView
)
