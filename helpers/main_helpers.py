import pandas as pd
import secrets
import sqlite3
import json

from schemas.input_schemas import (
	MeterByArea,
	SizingInputs,
	SizingInputsWithShared)

from pydantic import BaseModel
from typing import Union

from schemas.output_schemas import (
	MILPOutputs
)
from rec_sizing.custom_types.collective_milp_pool_types import (
	BackpackCollectivePoolDict,
	OutputsCollectivePoolDict
)


def generate_order_id() -> str:
	"""
	Return an unequivocal ID that identifies the request and can be used
	to retrieve the results later on
	:return: a token in string format
	"""
	return secrets.token_urlsafe(45)


def milp_inputs(user_params: Union[SizingInputs, SizingInputsWithShared],
				all_data_df: pd.core.frame.DataFrame) -> BackpackCollectivePoolDict:
	"""
	Auxiliary function to build the inputs for post-delivery MILP functions
	:param user_params:
	:param all_data_df: a pandas DataFrame with 6 columns: datetime, e_c, e_g, meter_id, buy_tariff and sell_tariff
	:return: structure ready to run the desired MILP
	"""
	meter_ids = all_data_df['meter_id'].unique()
	nr_time_steps = len(all_data_df['datetime'].unique())
	sizing_params = user_params.sizing_params_by_meter[0]

	all_data_df['datetime'] = pd.to_datetime(all_data_df['datetime'])

	print('all_data_df', all_data_df)

	meters = {
		meter_id: {
			"l_buy": all_data_df.loc[all_data_df['meter_id'] == meter_id].sort_values(['datetime'])['buy_tariff'].to_list(),
			"l_sell": all_data_df.loc[all_data_df['meter_id'] == meter_id].sort_values(['datetime'])['sell_tariff'].to_list(),
			"l_cont": 0.0,  # Populate with actual data
			"l_gic": sizing_params.l_gic,  # Populate with actual data
			"l_bic": sizing_params.l_bic,  # Populate with actual data
			"e_c": all_data_df.loc[all_data_df['meter_id'] == meter_id].sort_values(['datetime'])['e_c'].to_list(),
			"p_meter_max": 100,  # Populate with actual data
			"p_gn_init": 0.0,  # Populate with actual data
			'e_g_factor': all_data_df.loc[all_data_df['meter_id'] == meter_id].sort_values(['datetime'])['e_g'].to_list(),
			"p_gn_min": sizing_params.minimum_new_pv_power,
            "p_gn_max": sizing_params.maximum_new_pv_power,
            "e_bn_init": 0.0,  # Populate with actual data
            "e_bn_min": sizing_params.minimum_new_storage_capacity,
            "e_bn_max": sizing_params.maximum_new_storage_capacity,
            "soc_min": sizing_params.soc_min,
            "eff_bc": sizing_params.eff_bc,
            "eff_bd": sizing_params.eff_bd,
            "soc_max": sizing_params.soc_max,
            "deg_cost": sizing_params.deg_cost,
            "btm_evs": None,  # Populate with actual data
            "ewh": None  # Populate with actual data
		} for meter_id in meter_ids
	}
	with open('C:\\Users\\armando.moreno\\REC API\\rec_sizing_api\\helpers\\our_database.json', 'r') as f:
		l_grid = json.load(f)["l_grid"]

	backpack = BackpackCollectivePoolDict(
		nr_days=1/24,
		nr_clusters=1,
		l_grid=l_grid,
		delta_t=0.25,  # Assuming 15-minute intervals, change as needed
		storage_ratio=1.0,
		strict_pos_coeffs=False,
		total_share_coeffs=False,
		meters=meters
	)

	print('backpack: \n', backpack)

	return backpack


def milp_return_structure(cursor: sqlite3.Cursor,
						  order_id: str,
						  lem_organization: str) \
		-> MILPOutputs:
	"""
	Prepare the structure to be returned with the MILP outputs, in accordance with the API specifications
	:param cursor: cursor to the database
	:param order_id: order id provided by the user
	:param lem_organization: string indicating if LEM organization is "pool" or "bilateral"
	:return: structure with MILP outputs in the API specified outputs' format
	"""
	# Initialize the return structure
	milp_return = {
		'order_id': order_id,
	}

	# GENERAL MILP OUTPUTS #############################################################################################
	# Retrieve the general MILP outputs calculated for the order ID
	cursor.execute('''
		SELECT * FROM General_MILP_Outputs WHERE order_id = ?
	''', (order_id,))
	general_milp_outputs = cursor.fetchall()

	# Convert to dataframe for easy manipulation
	general_milp_outputs_df = pd.DataFrame(general_milp_outputs)
	general_milp_outputs_df.columns = ['index', 'order_id', 'objective_value', 'milp_status', 'total_rec_cost']
	del general_milp_outputs_df['index']
	del general_milp_outputs_df['order_id']

	# Create final dictionary substructure
	general_milp_outputs_dict = general_milp_outputs_df.to_dict('records')[0]

	# Update the return dictionary
	milp_return.update(general_milp_outputs_dict)

	# INDIVIDUAL COSTS #################################################################################################
	# Retrieve the individual costs calculated for the order ID
	cursor.execute('''
		SELECT * FROM Member_Costs WHERE order_id = ?
	''', (order_id,))
	member_costs = cursor.fetchall()

	# Convert to dataframe for easy manipulation
	member_costs_df = pd.DataFrame(member_costs)
	member_costs_df.columns = ['index', 'order_id', 'meter_id', 'member_cost', 'member_cost_compensation', 'member_savings']
	del member_costs_df['index']
	del member_costs_df['order_id']

	# Create final dictionary substructure
	member_costs_outputs_dict = {
		'member_costs': member_costs_df.to_dict('records')
	}

	# Update the return dictionary
	milp_return.update(member_costs_outputs_dict)



	# Meter Investments Outputs #################################################################################################
	# Retrieve the individual costs calculated for the order ID
	cursor.execute('''
		SELECT * FROM Meter_Investment_Outputs WHERE order_id = ?
	''', (order_id,))
	meter_investments_outputs = cursor.fetchall()

	# Convert to dataframe for easy manipulation
	meter_investments_outputs_df = pd.DataFrame(meter_investments_outputs)
	meter_investments_outputs_df.columns = ['index', 'order_id', 'meter_id', 'installation_cost', 'installation_cost_compensation', 'installation_savings',
				 'installed_pv', 'pv_investment_cost', 'installed_storage', 'storage_investment_cost', 'total_pv', 'total_storage',
				 'contracted_power', 'contracted_power_cost', 'retailer_exchange_costs', 'sc_tariffs_costs']
	del meter_investments_outputs_df['index']
	del meter_investments_outputs_df['order_id']

	# Create final dictionary substructure
	meter_investments_outputs_dict = {
		'meter_investments_outputs': meter_investments_outputs_df.to_dict('records')
	}

	# Update the return dictionary
	milp_return.update(meter_investments_outputs_dict)



	# METER INPUTS #####################################################################################################
	# Retrieve the meter inputs used in the order ID
	cursor.execute('''
		SELECT * FROM Meter_Operation_Inputs WHERE order_id = ?
	''', (order_id,))
	meter_inputs = cursor.fetchall()

	# Convert to dataframe for easy manipulation
	meter_inputs_df = pd.DataFrame(meter_inputs)
	meter_inputs_df.columns = ['index', 'order_id', 'meter_id', 'datetime',
							   'energy_generated', 'energy_consumed',
							   'buy_tariff', 'sell_tariff']
	del meter_inputs_df['index']
	del meter_inputs_df['order_id']

	# Create final dictionary substructure
	meter_inputs_dict = {
		'meter_operation_inputs': meter_inputs_df.to_dict('records')
	}

	# Update the return dictionary
	milp_return.update(meter_inputs_dict)

	# METER OUTPUTS ####################################################################################################
	# Retrieve the meter outputs calculated for the order ID
	cursor.execute('''
		SELECT * FROM Meter_Operation_Outputs WHERE order_id = ?
	''', (order_id,))
	meter_operation_outputs = cursor.fetchall()

	# Convert to dataframe for easy manipulation
	meter_operation_outputs_df = pd.DataFrame(meter_operation_outputs)
	print("DataFrame shape before setting columns:", meter_operation_outputs_df.shape)
	meter_operation_outputs_df.columns = ['index', 'order_id', 'meter_id', 'datetime',
							   'energy_surplus', 'energy_supplied', 'energy_purchased_lem', 'energy_sold_lem',
								'net_load', 'bess_energy_charged',
								'bess_energy_discharged', 'bess_energy_content']
	del meter_operation_outputs_df['index']
	del meter_operation_outputs_df['order_id']
	print("Existing columns:", meter_operation_outputs_df.columns)

	# Create final dictionary substructure
	meter_operation_outputs_dict = {
		'meter_operation_outputs': meter_operation_outputs_df.to_dict('records')
	}

	# Update the return dictionary
	milp_return.update(meter_operation_outputs_dict)




	# SELF CONSUMPTION TARIFFS #########################################################################################
	# Retrieve the self-consumption tariffs used for the order ID
	cursor.execute('''
		SELECT * FROM Pool_Self_Consumption_Tariffs WHERE order_id = ?
	''', (order_id,))
	self_consumption_tariffs = cursor.fetchall()

	# Convert to dataframe for easy manipulation
	self_consumption_tariff_df = pd.DataFrame(self_consumption_tariffs)
	self_consumption_tariff_df.columns = ['index', 'order_id', 'datetime', 'self_consumption_tariff']
	del self_consumption_tariff_df['index']
	del self_consumption_tariff_df['order_id']

	self_consumption_tariff_dict = {
		'self_consumption_tariffs': self_consumption_tariff_df.to_dict('records')
	}

	# Update the return dictionary
	milp_return.update(self_consumption_tariff_dict)

	# LEM PRICES #######################################################################################################
	# Retrieve the LEM prices calculated for the order ID
	cursor.execute('''
		SELECT * FROM Lem_Prices WHERE order_id = ?
	''', (order_id,))
	lem_prices = cursor.fetchall()

	# Convert to dataframe for easy manipulation
	lem_prices_df = pd.DataFrame(lem_prices)
	lem_prices_df.columns = ['index', 'order_id', 'datetime', 'value']
	del lem_prices_df['index']
	del lem_prices_df['order_id']

	lem_prices_dict = {
		'lem_prices': lem_prices_df.to_dict('records')
	}

	# Update the return dictionary
	milp_return.update(lem_prices_dict)

	return milp_return
