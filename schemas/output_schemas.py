from datetime import datetime as dt
from pydantic import (
	BaseModel,
	Field
)
from .enums import (
	OfferOrigin,
	OfferType
)


########################################################################################################################
# GENERAL RESPONSES
########################################################################################################################
class AcceptedResponse(BaseModel):
	message: str = Field(
		examples=['Processing has started. Use the order ID for status updates.']
	)
	order_id: str = Field(
		description='Order identifier for the request. <br />'
		            'Request results via REST API can only be retrieved by specifying this identifier.',
		examples=['iaMiULXA9BktPUu2b_PwTtycCSNe0_wYpPt9muwlEtgL49GDg-kggSktAjtu']
	)


class OrderNotProcessed(BaseModel):
	message: str = Field(
		examples=['Order found, but not yet processed. Please try again later.']
	)
	order_id: str = Field(
		max_length=45,
		min_length=45,
		description='Order identifier for the request.',
		examples=['iaMiULXA9BktPUu2b_PwTtycCSNe0_wYpPt9muwlEtgL49GDg-kggSktAjtu']
	)


class OrderNotFound(BaseModel):
	message: str = Field(
		examples=['Order not found.']
	)
	order_id: str = Field(
		max_length=45,
		min_length=45,
		description='Order identifier for the request.',
		examples=['iaMiULXA9BktPUu2b_PwTtycCSNe0_wYpPt9muwlEtgL49GDg-kggSktAjtu']
	)


class MemberIDNotFound(BaseModel):
	message: str = Field(
		examples=['One or more member IDs not found on registry system.']
	)
	order_id: str = Field(
		max_length=45,
		min_length=45,
		description='Order identifier for the request.',
		examples=['iaMiULXA9BktPUu2b_PwTtycCSNe0_wYpPt9muwlEtgL49GDg-kggSktAjtu']
	)


########################################################################################################################
# DATA RESPONSES
########################################################################################################################


class TotalCostRec(BaseModel):
	value: float = Field(description='Tocal Cost of the community, This includes the cost of each member installing its assets....')


class MemberCosts(BaseModel):
	member_id: str = Field(
		description='The string that unequivocally identifies the member of the REC that has ownserhip over the meter '
		            'making the offer.',
		examples=['Member#1']
	)
	costs: float = Field(description='Total Cost for that member....')
	savings: float = Field(description='Total Savings for that member....')


class CpeResults(BaseModel):
	cpe_id: str = Field(
		description='The string that identifies the CPE of the REC.',
		examples=['Prosumer#1']
	)
	installed_pv_power: float = Field(description='')
	installed_battery_capacity: float = Field(description='')
	contracted_power: float = Field(description='')
	total_pv: float = Field(description='')
	total_battery: float = Field(description='')


class OrderProcessed(BaseModel):
	order_id: str = Field(
		max_length=45,
		min_length=45,
		description='Order identifier for the request.',
		examples=['iaMiULXA9BktPUu2b_PwTtycCSNe0_wYpPt9muwlEtgL49GDg-kggSktAjtu']
	)
	total_cost_rec: TotalCostRec = Field(description='')
	members_costs: MemberCosts = Field(description='')
	cpe_results: list[CpeResults] = Field(description='')

# class InstalledPower(BaseModel):
# 	cpe_id: str = Field(
# 		description='The string that identifies the CPE of the REC'
# 		            'making the offer.',
# 		examples=['Prosumer#1']
# 	)
# 	value: float = Field(description='Tocal Cost of the community, This includes the cost of each member installing its assets....')
#
# class InstalledCapacity(BaseModel):
# 	cpe_id: str = Field(
# 		description='The string that identifies the CPE of the REC'
# 		            'making the offer.',
# 		examples=['Prosumer#1']
# 	)
# 	value: float = Field(description='Tocal Cost of the community, This includes the cost of each member installing its assets....')
#
#
# class ContractedPower(BaseModel):
# 	cpe_id: str = Field(
# 		description='The string that identifies the CPE of the REC'
# 		            'making the offer.',
# 		examples=['Prosumer#1']
# 	)
# 	value: float = Field(description='Tocal Cost of the community, This includes the cost of each member installing its assets....')
#
# class TotalPV(BaseModel):
# 	cpe_id: str = Field(
# 		description='The string that identifies the CPE of the REC'
# 		            'making the offer.',
# 		examples=['Prosumer#1']
# 	)
# 	value: float = Field(description='Tocal Cost of the community, This includes the cost of each member installing its assets....')
#
# class TotalBattery(BaseModel):
# 	cpe_id: str = Field(
# 		description='The string that identifies the CPE of the REC'
# 		            'making the offer.',
# 		examples=['Prosumer#1']
# 	)
# 	value: float = Field(description='Tocal Cost of the community, This includes the cost of each member installing its assets....')







# class LemPrice(BaseModel):
# 	datetime: dt = Field(
# 		description='Datetime in ISO 8601 format.'
# 	)
# 	value: float = Field(
# 		ge=0.0,
# 		description='Local energy market price computed, in €/kWh.'
# 	)
#
#
# class Offer(BaseModel):
# 	datetime: dt = Field(
# 		description='Datetime in ISO 8601 format.'
# 	)
# 	member_id: str = Field(
# 		description='The string that unequivocally identifies the member of the REC that has ownserhip over the meter '
# 		            'making the offer.',
# 		examples=['Member#1']
# 	)
# 	meter_id: str = Field(
# 		description='The string that unequivocally identifies the meter of the REC that made the offer.',
# 		examples=['Meter#1']
# 	)
# 	amount: float = Field(
# 		ge=0.0,
# 		description='Amount offered in the session, in kWh.'
# 	)
# 	value: float = Field(
# 		ge=0.0,
# 		description='Price offered in the session, in €/kwh.'
# 	)
# 	type: OfferType = Field(
# 		description='Indicates if it is a buying or selling offer.'
# 	)
# 	amount_origin: OfferOrigin = Field(
# 		description='Indicates if the amount of the offer is based on **registered** data or, when the same is not '
# 		            'available for this particular meter, if it came from **default** databases. <br />'
# 		            'For buying offers, the default database used for the meter\'s load profile is the portuguese DSO '
# 		            'E-Redes [typical consumption profiles](https://www.e-redes.pt/pt-pt/perfis-de-consumo). <br />'
# 		            'For selling offers, the default database used for the meter\'s generation profile (assumed to be '
# 		            'entirely composed of PV generation) is [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/).'
# 	)
# 	value_origin: OfferOrigin = Field(
# 		description='Indicates if the value of the offer is based on **registered** data or, when the same is not '
# 		            'available for this particular meter, if it came from **default** databases. <br />'
# 		            'The default values used are the regulated prices published by the portuguese energy services '
# 		            'regulator entity.'
# 		            '[ERSE](https://www.erse.pt/atividade/regulacao/tarifas-e-precos-eletricidade/).'
# 	)





	# lem_prices: list[LemPrice] = Field(
	# 	description='List with the local energy market prices computed for the requested horizon.'
	# )
	# offers: list[Offer] = Field(
	# 	description='A description of all the offers considered in the local energy market session that resulted in '
	# 	            'the calculated price.'
	# )




# class OrderProcessed(BaseModel):
# 	order_id: str = Field(
# 		max_length=45,
# 		min_length=45,
# 		description='Order identifier for the request.',
# 		examples=['iaMiULXA9BktPUu2b_PwTtycCSNe0_wYpPt9muwlEtgL49GDg-kggSktAjtu']
# 	)
# 	lem_prices: list[LemPrice] = Field(
# 		description='List with the local energy market prices computed for the requested horizon.'
# 	)
# 	offers: list[Offer] = Field(
# 		description='A description of all the offers considered in the local energy market session that resulted in '
# 		            'the calculated price.'
# 	)