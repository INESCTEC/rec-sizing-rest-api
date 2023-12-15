from datetime import datetime
from .enums import (
	BusinessModel,
	ObjectiveFunction,
	PriceMechanism,
	MarketMechanism,
	TypeofCommunity,
	BatteryFeaturesId,
	PvFeaturesId
)
from pydantic import (
	BaseModel,
	Field,
	field_validator
)
from pydantic_extra_types.coordinate import Coordinate
from typing import Set


class SizingInputs(BaseModel):
	start_datetime: datetime = Field(
		description='Start datetime for the sizing horizon (included in it) in ISO 8601 format.'
	)
	end_datetime: datetime = Field(
		description='End datetime for the sizing horizon (included in it) in ISO 8601 format.'
	)
	business_model: BusinessModel or None = Field(
		default=BusinessModel.all_market,
		description='There are two options: "all market" and "allocated". '
					'"allocated" means that installations with shared assets directly allocate their energy to their owners. '
					'On the other hand, "all market" means that the allocation of energy is not possible and all energy is shared and bought.'
	)
	objective_function: ObjectiveFunction or None = Field(
		default=ObjectiveFunction.arbitrage,
		description='There are two options: "arbitrage" and "self consumption". '
		'"arbitrage" means the minimization of all community costs'
		'"self consumption maximizes the self consumed energy in the community"'
	)
	shared_batteries: bool or None = Field(
		default=False,
		description='True means that installations with shared batteries are possible.'
	)
	shared_pv: bool or None = Field(
		default=False,
		description='True means that installations with shared PV systems are possible.'
	)
	price_mechanism: PriceMechanism or None = Field(
		default=PriceMechanism.crossingvalue,
		description='Three options:\n'
					'MMR: It is the mid-market rate. Price is the average of the highest selling opportunity costs with '
					'the lowest buying opportunity costs among all installations negotiating at a certain time period.\n'
					''
	)
	market_mechanism: MarketMechanism or None = Field(
		default=MarketMechanism.pool,
		description=''
	)
	sdr_compensation: float or None = Field(
		default=0.0,
		ge=0.0,
		le=1.0,
		description='Only considered when choosing "sdr" as the pricing mechanism. <br />'
		            'Defines a compensation between 0.0 and 1.0 allowing the user to set an incentive for internal '
		            'trades whenever the REC has a net surplus.'
	)
	mmr_divisor: int or None = Field(
		default=2,
		gt=0,
		description='Only considered when choosing "sdr" as the pricing mechanism. <br />'
		            'Defines the divisor considered on the MMR expression. Values greater than 2 will favor buyers '
		            'and values smaller than 2 will favor sellers.'
	)

	minimum_nr_members: int or None = Field(
		default=2,
		description=''
	)
	rec_location: Coordinate or None = Field(
		default={
			'latitude': 0.0,
			'longitude': 0.0
		},
		description=''
	)
	radius: int or None = Field(
		default=4,
		description=''
	)
	member_ids: Set[str] or None = Field(
		description='An array of strings that unequivocally identifies the members to be included in the REC. <br />'
		            'All registered assets (i.e., meter ids) belonging totally or partially to the members listed, '
		            'will be considered in the following computations.',
		examples=[('Member#1', 'Member#2')]
	)
	type_of_community: TypeofCommunity or None = Field(
		default=TypeofCommunity.cec,
		description=''
	)

	battery_features_id: BatteryFeaturesId or None = Field(
		default = BatteryFeaturesId.luna2000,
		description=''
	)
	pv_features_id: PvFeaturesId or None = Field(
		default=PvFeaturesId.pv1000,
		description=''
	)

	@field_validator('end_datetime')
	def is_end_after_start(cls, end_dt, values):
		start_dt = values.data['start_datetime']
		assert end_dt > start_dt, 'end_datetime <= start_datetime'
		return end_dt



# todo: adicionar função que valida se não foram enviados "member_ids", então é obrigatório ter
	#  enviado "rec_location"
