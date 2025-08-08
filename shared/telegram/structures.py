from dataclasses 	import dataclass

from shared.telegram.params import MessageParseMode


@dataclass
class Message:
	text: str
	parse_mode: MessageParseMode = MessageParseMode.HTML
