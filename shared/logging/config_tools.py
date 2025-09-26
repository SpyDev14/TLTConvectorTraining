"""
Инструменты для настройки конфига логирования
"""

from typing import Any

def add_global_filter(logging_conf: dict[str, Any], filter_name: str):
	if logging_conf.get('handlers', None) is None:
		return

	handlers: dict[str, dict] = logging_conf['handlers']

	for handler in handlers.values():
		if 'filters' not in handler:
			handler['filters'] = []
		handler['filters'].append(filter_name)
