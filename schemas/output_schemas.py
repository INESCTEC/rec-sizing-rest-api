from datetime import datetime as dt
from pydantic import (
	BaseModel,
	Field
)

from schemas.enums import MILPStatus


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


class MeterIDNotFound(BaseModel):
	message: str = Field(
		examples=['One or more meter IDs not found on registry system.']
	)
	order_id: str = Field(
		max_length=45,
		min_length=45,
		description='Order identifier for the request.',
		examples=['iaMiULXA9BktPUu2b_PwTtycCSNe0_wYpPt9muwlEtgL49GDg-kggSktAjtu']
	)


class TimeseriesDataNotFound(BaseModel):
	message: str = Field(
		examples=['One or more data point for one or more meter IDs not found on registry system.']
	)
	missing_data_points: dict[str, list[str]] = Field(
		description='Lists of missing data points\' datetime per meter ID.',
		examples=[{'Meter#1': ['2024-05-16T00:00:00Z', '2024-05-16T00:15:00Z']}]
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
# GEOGRAPHICAL ENDPOINT ################################################################################################
class MeterIDs(BaseModel):
	meter_ids: list[str] = Field(
		description='List with found meter ids within the area defined by the user.',
		examples=[['Meter#1', 'Meter#2']]
	)


# RETRIEVE SIZING ENDPOINT #############################################################################################
class IndividualCosts(BaseModel):
	meter_id: str = Field(
		description='The string that identifies the meter of the REC.',
		examples=['Meter#1']
	)
	individual_cost: float = Field(
		description='The total cost (operation + investment) for the optimization horizon calculated for the meter ID, '
					'without considering the cost for degradation of the BESS, in €.'
	)
	individual_savings: float = Field(
		description='Total savings obtained for that meter ID, in €. <br />'
					'This represents the difference between the cost obtained for the meter after running the sizing '
					'algorithm, considering the possibility to install new PV and/or storage capacities '
					'behind-the-meter, and the respective operation cost for the same period, without that possibility, '
					'i.e., by simply operating in an optimal fashion the assets that are already installed in the '
					'meter.'
	)


class InvestmentsPerMeter(BaseModel):
	meter_id: str = Field(
		description='The string that identifies the meter of the REC.',
		examples=['Meter#1']
	)
	individual_cost: float = Field(
		description='The total cost (operation + investment) for the optimization horizon calculated for the meter ID, '
					'without considering the cost for degradation of the BESS, in €.'
	)
	individual_savings: float = Field(
		description='Total savings obtained for that meter ID, in €. <br />'
					'This represents the difference between the cost obtained for the meter after running the sizing '
					'algorithm, considering the possibility to install new PV and/or storage capacities '
					'behind-the-meter, and the respective operation cost for the same period, without that possibility, '
					'i.e., by simply operating in an optimal fashion the assets that are already installed in the '
					'meter.'
	)
	installed_pv_power: float = Field(
		description='Newly installed PV power in the meter, in kW.'
	)
	installed_storage_capacity: float = Field(
		description='Newly installed storage capacity in the meter, in kWh.'
	)
	contracted_power: float = Field(
		description='Resulting Contracted Power for the meter, in kW. <br />'
					'Note: This value can be equal to or greater than the initial Contracted Power of the meter '
					'with the respective retailer. Any change to this value comes from newly installed capacities '
					'which are forecasted to require an additional power flow capacity at the meter.'
	)
	total_pv: float = Field(
		description='Total PV power in the meter, that equals the pre-installed capacity plus the '
					'newly installed capacity, in kW.'
	)
	total_storage: float = Field(
		description='Total storage capacity in the meter, that equals the pre-installed capacity plus the '
					'newly installed capacity, in kWh.'
	)


class InputsPerMeterAndDatetime(BaseModel):
	meter_id: str = Field(
		description='A string that unequivocally identifies a meter of the REC.',
		examples=['Meter#1']
	)
	datetime: dt = Field(
		description='Datetime in ISO 8601 format.',
		examples=['2024-05-16T00:45:00Z']
	)
	energy_generated: float = Field(
		description='PV panels’ generation considered by the algorithm, in kWh.',
		examples=[5.0]
	)
	energy_consumed: float = Field(
		description='Meter\'s consumption considered by the algorithm, in kWh.',
		examples=[5.0]
	)
	buy_tariff: float = Field(
		description='Purchase rate agreed with the retailer that was considered by the algorithm, in €/kWh.',
		examples=[5.0]
	)
	sell_tariff: float = Field(
		description='Selling rate agreed with the retailer that was considered by the algorithm, in €/kWh.',
		examples=[5.0]
	)


class OutputsPerMeterAndDatetime(BaseModel):
	meter_id: str = Field(
		description='A string that unequivocally identifies a meter of the REC.',
		examples=['Meter#1']
	)
	datetime: dt = Field(
		description='Datetime in ISO 8601 format.',
		examples=['2024-05-16T00:45:00Z']
	)
	energy_surplus: float = Field(
		description='Energy surplus that was sold to the retailer, in kWh.',
		examples=[5.0]
	)
	energy_supplied: float = Field(
		description='Energy supplied that was bought from the retailer, in kWh.',
		examples=[5.0]
	)
	energy_purchased_lem: float = Field(
		description='Energy that was purchased in the local energy market (LEM), in kWh.',
		examples=[5.0]
	)
	energy_sold_lem: float = Field(
		description='Energy that was sold in the local energy market (LEM), in kWh.',
		examples=[5.0]
	)
	net_load: float = Field(
		description='Expected net load registered in the meter, in kWh.',
		examples=[5.0]
	)
	bess_energy_charged: float = Field(
		description='Energy charged in the meter\'s BESS, in kWh. <br />'
					'Sent as 0.0 if the meter does not have storage.',
		examples=[5.0]
	)
	bess_energy_discharged: float = Field(
		description='Energy discharged in the meter\'s BESS, in kWh. <br />'
					'Sent as 0.0 if the meter does not have storage.',
		examples=[5.0]
	)
	bess_energy_content: float = Field(
		description='Energy content of the meter\'s BESS, at the end of the time interval, in kWh. <br />'
					'Sent as 0.0 if the meter does not have storage.',
		examples=[5.0]
	)


class SelfConsumptionTariffsPerDatetime(BaseModel):
	datetime: dt = Field(
		description='Datetime in ISO 8601 format.',
		examples=['2024-05-16T00:45:00Z']
	)
	self_consumption_tariff: float = Field(
		description='Tariff applicable to self-consumed energy from the public grid, '
					'published by the national regulatory entity for energy services, in €/kWh.',
		examples=[5.0]
	)


class LemPrice(BaseModel):
	datetime: dt = Field(
		description='Datetime in ISO 8601 format.',
		examples=['2024-05-16T00:45:00Z']
	)
	value: float = Field(
		ge=0.0,
		description='Local energy market price computed, in €/kWh.'
	)


class MILPOutputs(BaseModel):
	order_id: str = Field(
		max_length=45,
		min_length=45,
		description='Order identifier for the request.',
		examples=['iaMiULXA9BktPUu2b_PwTtycCSNe0_wYpPt9muwlEtgL49GDg-kggSktAjtu']
	)
	objective_value: float = Field(
		description='Objective value found for the MILP solution.',
		examples=[5.0]
	)
	milp_status: MILPStatus = Field(
		description='Indicates if the MILP was optimally solved (by returning "Optimal") or if an issue was raised '
					'and a successful solution was not achieved (by returning "Infeasible" or "Unbounded").'
	)
	total_rec_cost: float = Field(
		description='Total cost (operation + investment) for the whole community, in €.',
		examples=[5.0]
	)
	individual_costs: list[IndividualCosts] = Field(
		description='Individual total cost (operation + investment) per meter ID, in €.'
	)
	meter_investment_outputs: list[InvestmentsPerMeter] = Field(
		description='List of meters with the respective non time variable results.'
	)
	meter_operation_inputs: list[InputsPerMeterAndDatetime] = Field(
		description='All time-varying inputs that were fed into the MILP, per meter ID.'
	)
	meter_operation_outputs: list[OutputsPerMeterAndDatetime] = Field(
		description='Time-varying outputs calculated in the MILP, per meter ID.'
	)
	self_consumption_tariffs: list[SelfConsumptionTariffsPerDatetime] = Field(
		description='List with the self-consumption tariffs considered by the MILP.'
	)
	lem_prices: list[LemPrice] = Field(
		description='List with the local energy market prices computed for the requested horizon.'
	)
