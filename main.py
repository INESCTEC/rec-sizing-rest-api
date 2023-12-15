from helpers.generate_order_id import generate_order_id
from fastapi import (
	FastAPI,
	status,
	HTTPException
)
from fastapi.responses import JSONResponse
from schemas.input_schemas import (
	SizingInputs
)
from schemas.output_schemas import (
	AcceptedResponse,
	OrderProcessed,
	OrderNotFound,
	OrderNotProcessed,
	MemberIDNotFound
)


app = FastAPI(
	title='REC Sizing API',
	description='REST API for sizing a REC/CEC.',
	version='0.1.0'
)


@app.post('/sizing',
          description='',
          status_code=status.HTTP_202_ACCEPTED,
          tags=['Calculate Sizing'])
def compute_sizing(inputs_body: SizingInputs) -> AcceptedResponse:
	# todo: ir buscar os dados, correr sizing e, em paralelo retornar order_id
	order_id = generate_order_id()
	response = AcceptedResponse(
		message='Processing has started. Use the order ID for status updates.',
		order_id=order_id
	)
	return response

# # Example storage for orders
# orders_db = {}
# # Model for the order
# class OrderResult:
# 	def __init__(self, order_id: str, result: str, processed: bool = False, error: bool = False):
# 		self.order_id = order_id
# 		self.result = result
# 		self.processed = processed
# 		self.error = error
# @app.get('/sizing/{order_id}',
#          description='Endpoint for retrieving a request results\', provided the order ID.',
#          responses={
# 	         202: {'model': OrderNotProcessed, 'description': 'Order found but not yet processed.'},
# 	         404: {'model': OrderNotFound, 'description': 'Order not found.'},
# 	         412: {'model': MemberIDNotFound, 'description': 'One or more member IDs not found.'}
#          },
#          status_code=status.HTTP_200_OK,
#          tags=['Retrieve Sizing Results'])
# def get_sizing_results(order_id: str) -> OrderProcessed:
# 	# todo: no final apagar as linhas abaixo
# 	orders_db['123'] = OrderResult(order_id='123', result=None, processed=False)
# 	orders_db[order_id] = {
# 		'processed': True,
# 		'error': False,
# 		'order_id': order_id
# 	}
#
# 	# Check if the order_id exists in the database
# 	if order_id in orders_db:
# 		order = orders_db[order_id]
#
# 		# Check if the order is processed
# 		if order.processed:
# 			if order.error:
# 				raise HTTPException(status_code=412, detail='Precondition Failed.')
# 			else:
# 				# todo: acrescentar aqui a estrutura de resultados tal como definida em OrderProcessed
# 				return order
# 		else:
# 			# If the order is found but not processed, return 202 Accepted
# 			return JSONResponse(content={'message': 'Order found but not yet processed.',
# 			                             'order_id': order.order_id},
# 			                    status_code=status.HTTP_202_ACCEPTED)
# 	else:
# 		# If not found, raise an HTTPException with a 404 status code
# 		raise HTTPException(status_code=404, detail='Order not found.')






# Example storage for orders
orders_db = {}
# Model for the order
class OrderResult:
	def __init__(self, order_id: str, result: str, processed: bool = False, error: bool = False):
		self.order_id = order_id
		self.result = result
		self.processed = processed
		self.error = error

@app.get('/get_sizing/{order_id}',
         description='Endpoint for retrieving a request results\', provided the order ID.',
         responses={
	         202: {'model': OrderNotProcessed, 'description': 'Order found but not yet processed.'},
	         404: {'model': OrderNotFound, 'description': 'Order not found.'},
	         412: {'model': MemberIDNotFound, 'description': 'One or more member IDs not found.'}
         },
         status_code=status.HTTP_200_OK,
         tags=['Retrieve Sizing Results'])
def get_prices(order_id: str) -> OrderProcessed:
	orders_db['123'] = OrderResult(order_id='123', result=None, processed=False)
	# Check if the order_id exists in the database
	if order_id in orders_db:
		order = orders_db[order_id]

		# Check if the order is processed
		if order.processed:
			if order.error:
				raise HTTPException(status_code=412, detail='Precondition Failed.')
			else:
				return order
		else:
			# If the order is found but not processed, return 202 Accepted
			return JSONResponse(content={'message': 'Order found but not yet processed.',
			                             'order_id': order.order_id},
			                    status_code=status.HTTP_202_ACCEPTED)
	else:
		# If not found, raise an HTTPException with a 404 status code
		raise HTTPException(status_code=404, detail='Order not found.')
