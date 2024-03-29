CPU_stats = {
  "REGISTERS":"99999",
  "MEMORY": "99999",
  "DATABUS_WIDTH": "8",
  "RUN_RAM": False,
  "REMOVE_LABELS": False,
  "SHIFT_RAM": False,
  "SP_LOCATION": "0",
  "SP_IS_GPR": True,
  "REVERSED_STACK": False,
  "SP_VALUE": "63000",
  "KEEP_SP": False,
  "REG_ONLY": True,
  }
Instruction_table = {
  "ADD":  [1],
  "RSH":  [1],
  "NOR":  [1],
  "IMM":  [1], # <B> will be an immediate
  "LOD":  [1],
  "STR":  [1],
  "BGE":  [1],
  "IN":   [1], # <B> will be an immediate (port)
  "OUT":  [1], # <A> will be an immediate (port)
  }
def RawURCL(a, b):return a, b
def CleanURCL(a, b):return a, b