import pandas as pd
import secrets
import sqlite3
from typing import Union

from helpers.meter_contracted_powers import (
	INDATA_CONTRACTED_POWERS,
	SEL_CONTRACTED_POWERS
)
from helpers.meter_installed_pv import (
	INDATA_PV_INFO,
	SEL_PV_INFO
)
from rec_sizing.custom_types.collective_milp_pool_types import BackpackCollectivePoolDict
from schemas.input_schemas import (
	SizingInputs,
	SizingInputsWithShared
)
from schemas.output_schemas import (
	ClusteredMILPOutputs,
	MILPOutputs
)


def generate_order_id() -> str:
	"""
	Return an unequivocal ID that identifies the request and can be used
	to retrieve the results later on
	:return: a token in string format
	"""
	return secrets.token_urlsafe(45)


def milp_inputs(user_params: Union[SizingInputs, SizingInputsWithShared],
				all_data_df: pd.core.frame.DataFrame,
				self_cons_tariffs_series: pd.core.series.Series) -> BackpackCollectivePoolDict:
	"""
	Auxiliary function to build the inputs for post-delivery MILP functions
	:param user_params: hyperparameters passed by the user
	:param all_data_df: a pandas DataFrame with 6 columns: datetime, e_c, e_g, meter_id, buy_tariff and sell_tariff
	:param self_cons_tariffs_series: a pandas Series with the self consumption tariffs
	:return: structure ready to run the desired MILP
	"""
	meter_ids = all_data_df['meter_id'].unique()
	all_data_df.index.name = 'datetime'
	all_data_df.reset_index(inplace=True)
	sizing_params = user_params.sizing_params_by_meter
	try:
		sizing_params.extend(user_params.sizing_params_for_shared_meter)
	except AttributeError:
		pass

	# calculate the number of days in the data provided
	nr_meter_ids = len(meter_ids)
	nr_data_points = len(all_data_df) / nr_meter_ids
	assert nr_data_points % 96 == 0, 'horizon provided does not include full days'
	nr_days = int(nr_data_points / 96)

	# if nr_representative_days is 0, no clustering should be performed, so define it as the same as the number of days
	nr_clusters = nr_days if user_params.nr_representative_days == 0 else user_params.nr_representative_days

	# check the originally installed capacities
	dataset_origin = user_params.dataset_origin
	pv_info = SEL_PV_INFO if dataset_origin == 'SEL' else INDATA_PV_INFO
	contracted_powers_info = SEL_CONTRACTED_POWERS if dataset_origin == 'SEL' else INDATA_CONTRACTED_POWERS

	# build the meters structure separately
	meters = {}
	for meter_id in meter_ids:
		# get the hardcoded PV installed capacity for the meter;
		# if the meter ID is not in the list, it means it is a new "shared" meter ID, with no initial installed capacity
		p_gn_init = pv_info.get(meter_id) \
			if pv_info.get(meter_id) is not None \
			else 0

		# get the hardcoded contracted power for the meter;
		# if the meter ID is not in the list, it means it is a new "shared" meter ID, so get the value for "shared"
		p_meter_max = contracted_powers_info.get(meter_id) \
			if contracted_powers_info.get(meter_id) is not None \
			else contracted_powers_info.get('shared')

		meter_sizing_params = [x for x in sizing_params if x.meter_id == meter_id][0]

		meters[meter_id] = {
			"l_buy": all_data_df.loc[
				all_data_df['meter_id'] == meter_id].sort_values(['datetime'])['buy_tariff'].to_list(),
			"l_sell": all_data_df.loc[
				all_data_df['meter_id'] == meter_id].sort_values(['datetime'])['sell_tariff'].to_list(),
			"l_cont": 0.0462,  # todo: create separate structure with information per meter ID for INDATA and SEL
			"l_gic": meter_sizing_params.l_gic,
			"l_bic": meter_sizing_params.l_bic,
			"e_c": all_data_df.loc[
				all_data_df['meter_id'] == meter_id].sort_values(['datetime'])['e_c'].to_list(),
			"p_meter_max": p_meter_max,
			"p_gn_init": p_gn_init,
			'e_g_factor': all_data_df.loc[
				all_data_df['meter_id'] == meter_id].sort_values(['datetime'])['e_g'].to_list(),
			"p_gn_min": meter_sizing_params.minimum_new_pv_power,
			"p_gn_max": meter_sizing_params.maximum_new_pv_power,
			"e_bn_init": 0.0,  # no initial storage capacity is considered for any meter of any REC
			"e_bn_min": meter_sizing_params.minimum_new_storage_capacity,
			"e_bn_max": meter_sizing_params.maximum_new_storage_capacity,
			"soc_min": meter_sizing_params.soc_min,
			"eff_bc": meter_sizing_params.eff_bc,
			"eff_bd": meter_sizing_params.eff_bd,
			"soc_max": meter_sizing_params.soc_max,
			"deg_cost": meter_sizing_params.deg_cost
		}

	# build the self-consumption tariffs structure separately
	l_grid = self_cons_tariffs_series.to_list()

	# build the final inputs structure
	backpack = BackpackCollectivePoolDict(
		nr_days=nr_days,
		nr_clusters=nr_clusters,
		l_grid=l_grid,
		delta_t=0.25,
		storage_ratio=1.0,
		strict_pos_coeffs=True,
		total_share_coeffs=True,
		meters=meters
	)

	return backpack


def __common_milp_return_structure(cursor, order_id):
	"""
	Common output structure generation, for both clustered and non-clustered outputs.
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
	member_costs_df.columns = [
		'index', 'order_id', 'meter_id', 'member_cost', 'member_cost_compensation', 'member_savings'
	]
	del member_costs_df['index']
	del member_costs_df['order_id']

	# Create final dictionary substructure
	member_costs_outputs_dict = {
		'member_costs': member_costs_df.to_dict('records')
	}

	# Update the return dictionary
	milp_return.update(member_costs_outputs_dict)

	# Meter Investments Outputs ########################################################################################
	# Retrieve the individual costs calculated for the order ID
	cursor.execute('''
			SELECT * FROM Meter_Investment_Outputs WHERE order_id = ?
		''', (order_id,))
	meter_investment_outputs = cursor.fetchall()

	# Convert to dataframe for easy manipulation
	meter_investment_outputs_df = pd.DataFrame(meter_investment_outputs)
	meter_investment_outputs_df.columns = [
		'index', 'order_id', 'meter_id', 'installation_cost', 'installation_cost_compensation', 'installation_savings',
		'installed_pv', 'pv_investment_cost', 'installed_storage', 'storage_investment_cost', 'total_pv',
		'total_storage', 'contracted_power', 'contracted_power_cost', 'retailer_exchange_costs', 'sc_tariffs_costs']
	del meter_investment_outputs_df['index']
	del meter_investment_outputs_df['order_id']

	# Create final dictionary substructure
	meter_investment_outputs_dict = {
		'meter_investment_outputs': meter_investment_outputs_df.to_dict('records')
	}

	# Update the return dictionary
	milp_return.update(meter_investment_outputs_dict)

	return milp_return


def milp_return_structure(cursor: sqlite3.Cursor,
						  order_id: str) \
		-> MILPOutputs:
	"""
	Prepare the structure to be returned with the MILP outputs, in accordance with the API specifications
	:param cursor: cursor to the database
	:param order_id: order id provided by the user
	:return: structure with MILP outputs in the API specified outputs' format
	"""
	# Get non time-varying output structure:
	milp_return = __common_milp_return_structure(cursor, order_id)

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
	meter_operation_outputs_df.columns = ['index', 'order_id', 'meter_id', 'datetime',
							   'energy_surplus', 'energy_supplied', 'energy_purchased_lem', 'energy_sold_lem',
								'net_load', 'bess_energy_charged',
								'bess_energy_discharged', 'bess_energy_content']
	del meter_operation_outputs_df['index']
	del meter_operation_outputs_df['order_id']

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


def milp_return_clustered_structure(cursor: sqlite3.Cursor,
						  order_id: str) \
		-> ClusteredMILPOutputs:
	"""
	Prepare the structure to be returned with the (clustered) MILP outputs, in accordance with the API specifications
	:param cursor: cursor to the database
	:param order_id: order id provided by the user
	:return: structure with (clustered) MILP outputs in the API specified outputs' format
	"""
	# Get non time-varying output structure:
	milp_return = __common_milp_return_structure(cursor, order_id)

	# CLUSTERED METER INPUTS ###########################################################################################
	# Retrieve the (clustered) meter inputs used in the order ID
	cursor.execute('''
		SELECT * FROM Clustered_Meter_Operation_Inputs WHERE order_id = ?
	''', (order_id,))
	meter_inputs = cursor.fetchall()

	# Convert to dataframe for easy manipulation
	meter_inputs_df = pd.DataFrame(meter_inputs)
	meter_inputs_df.columns = ['index', 'order_id', 'meter_id', 'time', 'cluster_nr', 'cluster_weight',
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

	# CLUSTERED METER OUTPUTS ##########################################################################################
	# Retrieve the (clustered) meter outputs calculated for the order ID
	cursor.execute('''
		SELECT * FROM Clustered_Meter_Operation_Outputs WHERE order_id = ?
	''', (order_id,))
	meter_operation_outputs = cursor.fetchall()

	# Convert to dataframe for easy manipulation
	meter_operation_outputs_df = pd.DataFrame(meter_operation_outputs)
	meter_operation_outputs_df.columns = ['index', 'order_id', 'meter_id', 'time', 'cluster_nr', 'cluster_weight',
							   'energy_surplus', 'energy_supplied', 'energy_purchased_lem', 'energy_sold_lem',
								'net_load', 'bess_energy_charged',
								'bess_energy_discharged', 'bess_energy_content']
	del meter_operation_outputs_df['index']
	del meter_operation_outputs_df['order_id']

	# Create final dictionary substructure
	meter_operation_outputs_dict = {
		'meter_operation_outputs': meter_operation_outputs_df.to_dict('records')
	}

	# Update the return dictionary
	milp_return.update(meter_operation_outputs_dict)

	# CLUSTERED SELF CONSUMPTION TARIFFS ###############################################################################
	# Retrieve the (clustered) self-consumption tariffs used for the order ID
	cursor.execute('''
		SELECT * FROM Clustered_Pool_Self_Consumption_Tariffs WHERE order_id = ?
	''', (order_id,))
	self_consumption_tariffs = cursor.fetchall()

	# Convert to dataframe for easy manipulation
	self_consumption_tariff_df = pd.DataFrame(self_consumption_tariffs)
	self_consumption_tariff_df.columns = ['index', 'order_id', 'time', 'cluster_nr', 'cluster_weight',
										  'self_consumption_tariff']
	del self_consumption_tariff_df['index']
	del self_consumption_tariff_df['order_id']

	self_consumption_tariff_dict = {
		'self_consumption_tariffs': self_consumption_tariff_df.to_dict('records')
	}

	# Update the return dictionary
	milp_return.update(self_consumption_tariff_dict)

	# CLUSTERED LEM PRICES #############################################################################################
	# Retrieve the (clustered) LEM prices calculated for the order ID
	cursor.execute('''
		SELECT * FROM Clustered_Lem_Prices WHERE order_id = ?
	''', (order_id,))
	lem_prices = cursor.fetchall()

	# Convert to dataframe for easy manipulation
	lem_prices_df = pd.DataFrame(lem_prices)
	lem_prices_df.columns = ['index', 'order_id', 'time', 'cluster_nr', 'cluster_weight', 'value']
	del lem_prices_df['index']
	del lem_prices_df['order_id']

	lem_prices_dict = {
		'lem_prices': lem_prices_df.to_dict('records')
	}

	# Update the return dictionary
	milp_return.update(lem_prices_dict)

	return milp_return
