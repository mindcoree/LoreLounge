"""RabbitMQ integration for profile service."""

from importlib import import_module


_subscribers_registered = False


def register_broker_subscribers() -> None:
	"""Import subscriber modules once to register all RabbitMQ handlers."""
	global _subscribers_registered

	if _subscribers_registered:
		return

	import_module("infrastructure.broker.account_deletion")
	_subscribers_registered = True