import sqlite3

from loguru import logger
from rec_sizing.optimization_functions import run_pre_collective_pool_milp
from rec_sizing.post_processing_functions import run_post_processing
from helpers.dataspace_interactions import fetch_dataspace
from helpers.main_helpers import milp_inputs
from schemas.input_schemas import (SizingInputs, SizingInputsWithShared)
from typing import Union


def run_dual_thread(user_params: Union[SizingInputs, SizingInputsWithShared],
					id_order: str,
					conn: sqlite3.Connection,
					curs: sqlite3.Cursor):
	# get the necessary meters' data from the dataspace
	logger.info('Fetching data from dataspace.')
	data_df, sc_series, list_of_datetimes, missing_ids, missing_dts = fetch_dataspace(user_params)

	# if any missing meter ids or missing datetimes in the data for those meter ids was found,
	# update the database with an error and an indication of which data is missing
	if missing_ids:
		logger.warning('Missing meter IDs in dataspace.')
		message = f'One or more meter IDs not found on registry system: {missing_ids}'
		curs.execute('''
			UPDATE Orders
			SET processed = ?, error = ?, message = ?
			WHERE order_id = ?
		''', (True, '412', message, id_order))

	elif any(missing_dts.values()):
		logger.warning('Missing data points in dataspace.')
		missing_pairs = {k: v for k, v in missing_dts.items() if v}
		message = f'One or more data point for one or more meter IDs not found on registry system: {missing_pairs}'
		curs.execute('''
			UPDATE Orders
			SET processed = ?, error = ?, message = ?
			WHERE order_id = ?
		''', (True, '422', message, id_order))

	# otherwise, proceed normally
	else:
		# get the set of meter ids requested
		meter_ids = set(data_df['meter_id'])
		# prepare the inputs for the MILP
		logger.info('Building inputs.')
		inputs = milp_inputs(user_params, data_df, sc_series)
		# run optimization
		logger.info('Running MILP.')
		results = run_pre_collective_pool_milp(inputs)
		# Create the INPUTS_OWNERSHIP_PP dictionary
		INPUTS_OWNERSHIP_PP = {'ownership': {}}
		if hasattr(user_params, 'shared_meter_id'):
			for meter in [i for i in meter_ids if i != user_params.shared_meter_id]:
				# Add the percentage for the meter
				INPUTS_OWNERSHIP_PP['ownership'][meter] = {meter: 1.0}
		else:
			for meter in meter_ids:
				# Add the percentage for the meter
				INPUTS_OWNERSHIP_PP['ownership'][meter] = {meter: 1.0}

		if hasattr(user_params, 'shared_meter_id'):
			# Add shared meter ownership
			for i, ownership in enumerate(user_params.ownerships, start=1):
				meter_id = ownership.meter_id
				percentage = ownership.percentage
				# Calculate the shared meter ownership percentage
				shared_meter_ownership = {meter_id: percentage / 100}
			shared_meter_key = user_params.shared_meter_id
			# Add shared meter ownership to INPUTS_OWNERSHIP_PP
			INPUTS_OWNERSHIP_PP['ownership'][shared_meter_key] = shared_meter_ownership

		results_pp = run_post_processing(results, inputs, INPUTS_OWNERSHIP_PP)

		# update the database with the new order ID
		logger.info('Updating database with results.')
		curs.execute('''
			UPDATE Orders
			SET processed = ?
			WHERE order_id = ?
		''', (True, id_order))

		curs.execute('''
			INSERT INTO General_MILP_Outputs (order_id, objective_value, milp_status, total_rec_cost)
			VALUES (?, ?, ?, ?)
		''', (
			id_order,
			round(results_pp['obj_value'], 2),
			results['milp_status'],
			round(results_pp['obj_value'], 2)
		))
		# todo: this
		if hasattr(user_params, 'shared_meter_id'):
			for meter_id in [i for i in meter_ids if i != user_params.shared_meter_id]:
				curs.execute('''
					INSERT INTO Member_Costs (order_id, meter_id, member_cost, member_cost_compensation, member_savings)
					VALUES (?, ?, ?, ?, ?)
				''', (
					id_order,
					meter_id,
					round(results_pp['member_cost'][meter_id], 2),
					round(results_pp['member_cost_compensations'][meter_id], 2),
					0
				))
		else:
			for meter_id in meter_ids:
				curs.execute('''
									INSERT INTO Member_Costs (order_id, meter_id, member_cost, member_cost_compensation, member_savings)
									VALUES (?, ?, ?, ?, ?)
								''', (
					id_order,
					meter_id,
					round(results_pp['member_cost'][meter_id], 2),
					round(results_pp['member_cost_compensations'][meter_id], 2),
					0
				))

		for meter_id in meter_ids:
			curs.execute('''
				INSERT INTO Meter_Investment_Outputs (
				order_id, meter_id, installation_cost, installation_cost_compensation, installation_savings, 
				installed_pv, pv_investment_cost, installed_storage, storage_investment_cost, total_pv, total_storage, 
				contracted_power, contracted_power_cost, retailer_exchange_costs, sc_tariffs_costs)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
			''', (
				id_order,
				meter_id,
				round(results_pp['installation_cost_compensations'][meter_id], 3),
				round(results_pp['installation_cost_compensations'][meter_id], 3),
				0,
				round(results_pp['p_gn_new'][meter_id], 3),
				round(results_pp['PV_investments_cost'][meter_id], 3),
				round(results_pp['e_bn_new'][meter_id], 3),
				round(results_pp['batteries_investments_cost'][meter_id], 3),
				round(results_pp['p_gn_total'][meter_id], 3),
				round(results_pp['e_bn_total'][meter_id], 3),
				round(results_pp['p_cont'][meter_id], 3),
				round(results_pp['contractedpower_cost'][meter_id], 3),
				round(sum(results_pp['e_sup'][meter_id]), 3),
				round(sum(results_pp['e_slc_pool'][meter_id]), 3)
			))

		for idx, dt in enumerate(list_of_datetimes):

			curs.execute('''
				INSERT INTO Lem_Prices (order_id, datetime, value)
				VALUES (?, ?, ?)
			''', (
				id_order,
				dt,
				round(results_pp['dual_prices'][idx], 3)
			))

			curs.execute('''
				INSERT INTO Pool_Self_Consumption_Tariffs (order_id, datetime, self_consumption_tariff)
				VALUES (?, ?, ?)
			''', (
				id_order,
				dt,
				round(inputs['l_grid'][idx], 3)
			))

			# todo: energy_generated é, na verdade,e_g_factor
			for meter_id in meter_ids:
				curs.execute('''
					INSERT INTO Meter_Operation_Inputs (order_id, meter_id, datetime, energy_generated, 
						energy_consumed, buy_tariff, sell_tariff)
					VALUES (?, ?, ?, ?, ?, ?, ?)
				''', (
					id_order,
					meter_id,
					dt,
					round(inputs['meters'][meter_id]['e_g_factor'][idx], 3),
					round(inputs['meters'][meter_id]['e_c'][idx], 3),
					round(inputs['meters'][meter_id]['l_buy'][idx], 3),
					round(inputs['meters'][meter_id]['l_sell'][idx], 3),
				))

				curs.execute('''
					INSERT INTO Meter_Operation_Outputs (order_id, meter_id, datetime, energy_surplus, 
						energy_supplied, energy_purchased_lem, energy_sold_lem, net_load, 
						bess_energy_charged, bess_energy_discharged, bess_energy_content)
					VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
				''', (
					id_order,
					meter_id,
					dt,
					round(results_pp['e_sur'][meter_id][idx], 3),
					round(results_pp['e_sup'][meter_id][idx], 3),
					round(results_pp['e_pur_pool'][meter_id][idx], 3),
					round(results_pp['e_sale_pool'][meter_id][idx], 3),
					round(results['e_cmet'][meter_id][idx], 3),
					round(results_pp['e_bc'][meter_id][idx], 3),
					round(results_pp['e_bd'][meter_id][idx], 3),
					round(results_pp['e_bat'][meter_id][idx], 3)
				))

		conn.commit()

		logger.info('Finished!')
