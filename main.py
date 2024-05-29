from helpers.generate_order_id import generate_order_id
from loguru import logger

from fastapi import (
	FastAPI,
	status
)
from fastapi.responses import JSONResponse

from helpers.log_setting import (
	remove_logfile_handler,
	set_logfile_handler,
	set_stdout_logger
)
from schemas.input_schemas import (
	MeterByArea,
	SizingInputs,
	SizingInputsWithShared
)
from schemas.output_schemas import (
	AcceptedResponse,
	OrderNotFound,
	OrderNotProcessed,
	MeterIDNotFound,
	MILPOutputs,
	TimeseriesDataNotFound,
	MeterIDs
)


# Initialize the app
app = FastAPI(
	title='REC Sizing API',
	description='REST API for sizing a REC.',
	version='0.2.0'
)


# Runs when the API is started: set loggers and create / connect to SQLite database ####################################
@app.on_event('startup')
def startup_event():
	# Set up logging
	set_stdout_logger()
	app.state.handler = set_logfile_handler('logs')


# Runs when the API is closed: remove logger handlers and disconnect SQLite database ###################################
@app.on_event('shutdown')
def shutdown_event():
	# Remove all handlers associated with the logger object
	remove_logfile_handler(app.state.handler)


# GEOGRAPHICAL ENDPOINT ################################################################################################
@app.post('/search_meters_in_area',
		  description='Search which meters are located within the geographical '
					  'circle formed by a point [lat, long] and a radius.',
		  status_code=status.HTTP_200_OK,
		  tags=['Search Meter IDs'])
def search_meters_in_area(inputs_body: MeterByArea) -> MeterIDs:
	logger.info('[API] Computing REC area and finding meter IDs within that area.')
	# todo: include function to calculate an area based on the provided inputs
	#  and check which meter IDs are within thar area
	found_meters = []

	return JSONResponse(content={'meter_ids': found_meters},
						status_code=status.HTTP_200_OK)


# LAUNCH SIZING ENDPOINTS ##############################################################################################
@app.post('/sizing_with_shared_asset',
          description='Perform a sizing MILP where shared assets are considered, '
					  'i.e., an additional meter ID is included within the REC where a new PV and/or storage '
					  'asset can be potentially installed.',
          status_code=status.HTTP_202_ACCEPTED,
          tags=['Calculate Sizing'])
def compute_sizing_with_shared_resources(inputs_body: SizingInputsWithShared) -> AcceptedResponse:
	# generate an order ID for the user to fetch the results when ready
	logger.info('[API] Generating unique order ID.')
	id_order = generate_order_id()

	return JSONResponse(content={'message': 'Processing has started. Use the order ID for status updates.',
								 'order_id': id_order},
						status_code=status.HTTP_202_ACCEPTED)


@app.post('/sizing_without_shared_assets',
          description='Perform a sizing MILP where shared assets are not considered, '
					  'i.e., new installed PV and/or storage capacities are limited '
					  'to the existing meter IDs within the REC.',
          status_code=status.HTTP_202_ACCEPTED,
          tags=['Calculate Sizing'])
def compute_sizing_without_shared_resources(inputs_body: SizingInputs) -> AcceptedResponse:
	# generate an order ID for the user to fetch the results when ready
	logger.info('[API] Generating unique order ID.')
	id_order = generate_order_id()

	return JSONResponse(content={'message': 'Processing has started. Use the order ID for status updates.',
								 'order_id': id_order},
						status_code=status.HTTP_202_ACCEPTED)


# RETRIEVE SIZING ENDPOINT #############################################################################################
@app.get('/get_sizing/{order_id}',
         summary='Get Sizing Results',
         description='Endpoint for retrieving the sizing results\', provided the order ID.',
		 responses={
			 202: {'model': OrderNotProcessed, 'description': 'Order found but not yet processed.'},
			 404: {'model': OrderNotFound, 'description': 'Order not found.'},
			 412: {'model': MeterIDNotFound, 'description': 'One or more meter IDs not found.'},
			 422: {'model': TimeseriesDataNotFound,
				   'description': 'One or more data point for one or more meter IDs not found.'}
		 },
         status_code=status.HTTP_200_OK,
         tags=['Retrieve Sizing Results'])
def get_sizing_results(order_id: str) -> MILPOutputs:
	# Check if the order_id exists in the database
	logger.info('[API] Searching for order ID in local database.')

	# If the order is not found, return 404 Not Found
	return JSONResponse(content={'message': 'Order not found.',
								 'order_id': order_id},
						status_code=status.HTTP_404_NOT_FOUND)


if __name__ == '__main__':
	import uvicorn
	uvicorn.run(app, host="127.0.0.1", port=8000)
