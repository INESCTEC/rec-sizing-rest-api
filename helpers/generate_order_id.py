import secrets


def generate_order_id():
	"""
	Return an unequivocal ID that identifies the request and can be used
	to retrieve the results later on
	:return: a token in string format
	"""
	return secrets.token_urlsafe(45)
