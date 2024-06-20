from datetime import datetime
from itertools import islice
from pydantic import (
	BaseModel,
	Field,
	field_validator
)
from pydantic_extra_types.coordinate import Coordinate
from typing import (
	List,
	Set
)


# GEOGRAPHICAL ENDPOINT ################################################################################################
class MeterByArea(BaseModel):
	rec_location: Coordinate or None = Field(
		default={
			'latitude': 0.0,
			'longitude': 0.0
		},
		description='Latitude and Longitude of the REC.'
	)
	radius: int or None = Field(
		default=4,
		ge=0,
		description='Radius, in km, that gives origin to a circle with the center in Latitude and Longitude. Meters '
					'within this circle will be retrieved from dataspace to form the REC.'
	)


# LAUNCH SIZING ENDPOINTS ##############################################################################################
class SizingParameters(BaseModel):
	power_energy_ratio: float = Field(
		description='Power/energy [kW/kWh] ratio of the newly installed storage capacity. '
					'E.g., if the asset is to be able to charge/discharge in 1h, this ratio should be sent as 1.0, '
					'for 30 minutes this ratio should be 0.5 and for 2h this ratio should be 2.0.',
		examples=[1.0]
	)
	minimum_new_pv_power: float = Field(
		description='Minimum newly installed PV capacity, in kW. <br />'
					'Note: if no new PV capacity is to be installed set this value to 0.0.',
		examples=[0.0]
	)
	maximum_new_pv_power: float = Field(
		description='Maximum newly installed PV capacity, in kW. <br />'
					'Note: if no new PV capacity is to be installed set this value to 0.0.',
		examples=[10.0]
	)
	minimum_new_storage_capacity: float = Field(
		description='Minimum newly installed storage capacity, in kWh. <br />'
					'Note: if no new storage capacity is to be installed set this value to 0.0.',
		examples=[0.0]
	)
	maximum_new_storage_capacity: float = Field(
		description='Maximum newly installed storage capacity, in kWh. <br />'
					'Note: if no new storage capacity is to be installed set this value to 0.0.',
		examples=[10.0]
	)
	l_gic: float = Field(
		description='Cost of installing new PV, in €/kW. <br />',
		examples=[10.0]
	)
	l_bic: float = Field(
		description='Cost of installing new battery capacity, in €/kWh. <br />',
		examples=[10.0]
	)
	soc_min: float = Field(
		description='Minimum state-of-charge of the battery to be installed, in %. <br />',
		examples=[10.0]
	)
	soc_max: float = Field(
		description='Maximum state-of-charge of the battery to be installed, in %. <br />',
		examples=[10.0]
	)
	eff_bc: float = Field(
		description='Charging efficiency of the battery to be installed, in %. <br />',
		examples=[10.0]
	)
	eff_bd: float = Field(
		description='Discharging efficiency of the battery to be installed, in %. <br />',
		examples=[10.0]
	)
	deg_cost: float = Field(
		description='Degradation cost of the battery to be installed, in %. <br />'
					'Note: if no new storage capacity is to be installed set this value to 0.0.',
		examples=[10.0]
	)

class SizingParametersByMeter(SizingParameters):
	meter_id: str = Field(
		description='The string that unequivocally identifies the meter ID of the REC.',
		examples=['Meter#1']
	)


class SizingInputs(BaseModel):
	start_datetime: datetime = Field(
		description='Start date for the sizing horizon (included in it) in ISO 8601 format.',
		examples=['2024-05-16 00:00:00']
	)
	end_datetime: datetime = Field(
		description='End date for the sizing horizon (included in it) in ISO 8601 format.',
		examples=['2024-05-16 00:45:00']
	)
	nr_representative_days: int = Field(
		ge=0,
		description='If the user defines a number > 0, a clustering of the input data is performed prior to the '
					'MILP run and sizing is performed over the number of representative days here defined. '
					'If the user defines this number as 0, no clustering is performed.'
					'Note: If the user defines a number of representative days greater than the number of days in the '
					'historical data sets, clustering is not performed.'
	)
	meter_ids: Set[str] = Field(
		description='An array of strings that unequivocally identifies the meters to be included in the REC. <br />'
					'All registered assets (i.e., meter ids) belonging to the meters listed, will be considered when '
					'running the algorithm.',
		examples=[('Meter#1', 'Meter#2')]
	)
	sizing_params_by_meter: List[SizingParametersByMeter] = Field(
		description='List with parameterization for potentially new installed PV and/or storage capacities '
					'behind the meter IDs of the REC.'
	)

	@field_validator('end_datetime')
	def is_end_after_start(cls, end_dt, values):
		start_dt = values.data['start_datetime']
		assert end_dt > start_dt, 'end_datetime <= start_datetime'
		return end_dt


class Ownership(BaseModel):
	meter_id: str = Field(
		description='The string that unequivocally identifies the meter ID '
					'that has ownership over the new shared meter ID.',
		examples=['Meter#1']
	)
	percentage: float = Field(
		ge=0.0,
		le=100.0,
		description='Ownership percentage that the meter ID owner will have over the new shared meter.'
	)


class SizingInputsWithShared(SizingInputs):
	shared_meter_id: str = Field(
		description='The string that unequivocally identifies the meter ID that will be shared.',
		examples=["Meter#3"]
	)
	ownerships: List[Ownership] = Field(
		description='List of ownership percentages of meter ID responsible for the new shared meter. '
					'Note: meter ID that don\'t have a percentage over the new meter are not required '
					'to be defined on this list, but the sum of all ownerships must equal 100%.'
	)
	sizing_params_for_shared_meter: SizingParameters = Field(
		description='List with parameterization for potentially new installed PV and/or storage capacities '
					'behind a new shared meter ID within the REC.'
	)

	@field_validator('ownerships')
	def ownerships_sum(cls, ownerships):
		# Assert that the structure only has unique meter IDs
		meter_ids = [ownership.meter_id for ownership in ownerships]
		dup_ids = set([x for pos, x in enumerate(meter_ids) if x in islice(meter_ids, pos+1, None)])
		assert not dup_ids, f'Found duplicated meter IDs: {list(dup_ids)}'

		# Assert that the total ownership percentages over the shared meter total 100%
		total_percentage = sum([ownership.percentage for ownership in ownerships])
		assert total_percentage == 100.0, 'The sum of all ownerships must equal 100%.'

		return ownerships
