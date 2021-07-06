CPU_stats = {
  "REGISTERS":"",
  "MEMORY": "",
  "DATABUS_WIDTH": "",
  "RUN_RAM": True,
  "REMOVE_LABELS": False,
  "SHIFT_RAM": False,
  "SP_LOCATION": "",
  "SP_IS_GPR": True,
  "REVERSED_STACK": False,
  "SP_VALUE": "",
  "KEEP_SP": False,
  }
Instruction_table = {
  # Bare minimum, fill in all of these
  "ADD": [],
  "IMM": [], # <B> will be an immediate (number)
  "BGE": [],
  "LOD": [],
  "STR": [],
  "RSH": [],
  "NOR": [],
  # Required, but less common
  "IN":  [], # <B> will be an immediate (port)
  "OUT": [], # <A> will be an immediate (port)
  "DW":  [], # Only for RUN RAM
  # Strongly recommended
  "SUB": [],
  "JMP": [],
  "MOV": [],
  "INC": [],
  "DEC": [],
  "HLT": [],
  "BRZ": [],
  "BNZ": [],
  "BOD": [],
  "BEV": [],
  "STR_ri": [],
  # Recommended
  "AND": [],
  "OR": [],
  "XOR": [],
  "PSH": [],
  "POP": [],
  "LSH": [],
  "CAL": [],
  "RET": [],
  }
Port_table = {
  "%NUMB": 0,
  "%TEXT": 0
}
from URCL import instruction, opcode, operand
def RawURCL(a, b):
  return a, b
def CleanURCL(a, b):
  return a, b
def LabelISA(code):
  return code
def FinalISA(code):
  return code