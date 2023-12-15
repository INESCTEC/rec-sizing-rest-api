from enum import Enum


class BusinessModel(str, Enum):
	all_market = 'all market'
	allocated = 'allocated'


class ObjectiveFunction(str, Enum):
	self_consumption = 'self-consumption'
	arbitrage = 'arbitrage'

class PriceMechanism(str, Enum):
	MMR = 'MMR'
	SDR = 'SDR'
	crossingvalue = 'crossing value'

class MarketMechanism(str, Enum):
	pool = 'Pool'
	bilateral = 'Bilateral'

class TypeofCommunity(str, Enum):
	rec = 'REC'
	cec = 'CEC'


class BatteryFeaturesId(str, Enum):
	luna2000 = 'Luna2000'
	luna3000 = 'Luna3000'

class PvFeaturesId(str, Enum):
	pv1000='PV1000'
	pv2000 = 'PV2000'

class OfferType(str, Enum):
	buy = 'buy'
	sell = 'sell'


class OfferOrigin(str, Enum):
	registered = 'registered'
	default = 'default'
