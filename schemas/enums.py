from enum import Enum


class DatasetOrigin(str, Enum):
	ceve = 'CEVE'
	sel = 'SEL'


class MILPStatus(str, Enum):
	optimal = 'Optimal',
	unbounded = 'Unbounded',
	infeasible = 'Infeasible'
