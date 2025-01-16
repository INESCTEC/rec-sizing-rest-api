from enum import Enum


class DatasetOrigin(str, Enum):
	indata = 'IN-DATA'
	sel = 'SEL'


class MILPStatus(str, Enum):
	optimal = 'Optimal',
	unbounded = 'Unbounded',
	infeasible = 'Infeasible'
