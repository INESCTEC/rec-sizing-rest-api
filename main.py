import threading
import warnings

from fastapi import (
	FastAPI,
	status
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from helpers.database_interactions import connect_to_sqlite_db
from helpers.dataspace_interactions import fetch_meters_location
from helpers.log_setting import (
	remove_logfile_handler,
	set_logfile_handler,
	set_stdout_logger
)
from helpers.main_helpers import (
	generate_order_id,
	milp_return_structure
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
from threads.run_milp_thread import run_dual_thread


# Silence deprecation warning for startup and shutdown events
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Initialize the app
app = FastAPI(
	title='REC Sizing API',
	description='REST API for sizing a REC.',
	version='0.2.0'
)

# To avoid CORS problem, where the UI makes an initial OPTIONS request
app.add_middleware(
   CORSMiddleware,
   allow_origins=["http://localhost:5173",],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

# Set up logging
set_stdout_logger()
app.state.handler = set_logfile_handler('logs')


# Runs when the API is started: set loggers and create / connect to SQLite database ####################################
@app.on_event('startup')
def startup_event():
	# Set up logging
	set_stdout_logger()
	app.state.handler = set_logfile_handler('logs')

	# Get cursor and connection to SQLite database
	app.state.conn, app.state.cursor = connect_to_sqlite_db()


# Runs when the API is closed: remove logger handlers and disconnect SQLite database ###################################
@app.on_event('shutdown')
def shutdown_event():
	# Remove all handlers associated with the logger object
	remove_logfile_handler(app.state.handler)

	# Get cursor and connection to SQLite database
	app.state.conn.close()


# GEOGRAPHICAL ENDPOINT ################################################################################################
@app.post('/search_meters_in_area',
		  description='Search which meters are located within the geographical '
					  'circle formed by a point [lat, long] and a radius.',
		  status_code=status.HTTP_200_OK,
		  tags=['Search Meter IDs'])
def search_meters_in_area(inputs_body: MeterByArea) -> MeterIDs:
	logger.info('Computing REC area and finding meter IDs within that area.')
	found_meters = fetch_meters_location(inputs_body)
	return JSONResponse(content=found_meters.dict(), status_code=status.HTTP_200_OK)


# LAUNCH SIZING ENDPOINTS ##############################################################################################
@app.post('/sizing_with_shared_assets',
          description='Perform a sizing MILP where shared assets are considered, '
					  'i.e., an additional meter ID is included within the REC where a new PV and/or storage '
					  'asset can be potentially installed.',
          status_code=status.HTTP_202_ACCEPTED,
          tags=['Calculate Sizing'])
def compute_sizing_with_shared_resources(inputs_body: SizingInputsWithShared) -> AcceptedResponse:
	# generate an order ID for the user to fetch the results when ready
	logger.info('Generating unique order ID.')
	id_order = generate_order_id()

	# update the database with the new order ID
	logger.info('Creating registry in database for new order ID.')
	app.state.cursor.execute('''
				INSERT INTO Orders (order_id, processed, error, message)
				VALUES (?, ?, ?, ?)
			''', (id_order, False, '', ''))
	app.state.conn.commit()

	# initiate a parallel process (thread) to start computing the prices
	# while a message is immediately sent to the user
	logger.info('Launching thread.')
	threading.Thread(target=run_dual_thread,
					 args=(inputs_body, id_order, app.state.conn, app.state.cursor)).start()

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
	logger.info('Generating unique order ID.')
	id_order = generate_order_id()

	# update the database with the new order ID
	logger.info('Creating registry in database for new order ID.')
	app.state.cursor.execute('''
				INSERT INTO Orders (order_id, processed, error, message)
				VALUES (?, ?, ?, ?)
			''', (id_order, False, '', ''))
	app.state.conn.commit()

	# initiate a parallel process (thread) to start computing the prices
	# while a message is immediately sent to the user
	logger.info('Launching thread.')
	threading.Thread(target=run_dual_thread,
					 args=(inputs_body, id_order, app.state.conn, app.state.cursor)).start()

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
	logger.info('Searching for order ID in local database.')
	app.state.cursor.execute('''
		SELECT * FROM Orders WHERE order_id = ?
	''', (order_id,))

	# Fetch one row
	order = app.state.cursor.fetchone()

	if order is not None:
		logger.info('Order ID found. Checking if order has already been processed.')
		processed = bool(order[1])
		error = order[2]
		message = order[3]

		# Check if the order is processed
		if processed:
			logger.info('Order ID processed. Checking if process raised error.')
			if error == '412':
				# If the order is found but was met with missing meter ID(s)
				return JSONResponse(content={'message': message,
											 'order_id': order_id},
									status_code=status.HTTP_412_PRECONDITION_FAILED)

			elif error == '422':
				# If the order is found but was met with missing data point(s)
				return JSONResponse(content={'message': message,
											 'order_id': order_id},
									status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

			else:
				logger.info('Order ID correctly processed. Fetching outputs.')
				# If the order resulted from a request to a "vanilla" endpoint,
				# prepare the response message accordingly
				milp_return = milp_return_structure(app.state.cursor, order_id)

				return JSONResponse(content=milp_return,
									status_code=status.HTTP_200_OK)

		else:
			# If the order is found but not processed, return 202 Accepted
			return JSONResponse(content={'message': 'Order found but not yet processed.',
										 'order_id': order_id},
								status_code=status.HTTP_202_ACCEPTED)

	else:
		# If the order is not found, return 404 Not Found
		return JSONResponse(content={'message': 'Order not found.',
									 'order_id': order_id},
							status_code=status.HTTP_404_NOT_FOUND)


if __name__ == '__main__':
	import uvicorn
	import os

	host = os.getenv("SIZING_HOST", "127.0.0.1")
	port = int(os.getenv("SIZING_PORT", 8001))
	uvicorn.run(app, host=host, port=port)
