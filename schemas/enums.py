from enum import Enum


class MILPStatus(str, Enum):
	optimal = 'Optimal',
	unbounded = 'Unbounded',
	infeasible = 'Infeasible'
