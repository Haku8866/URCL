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
  "SP_VALUE": "0",
  "KEEP_SP": False,
  }
Instruction_table = {
  "ADD":  [1],
  "RSH":  [1],
  "NOR":  [1],
  "IMM":  [1], # <B> will be an immediate
  "LOD":  [1],
  "DBLE_LOD":  [1],
  "STR":  [1],
  "DBLE_STR":  [1],
  "BGE":  [1],
  "DBLE_BGE": [1],
  "DW":   [1], # Only for RUN RAM
  "IN":   [1], # <B> will be an immediate (port)
  "OUT":  [1], # <A> will be an immediate (port)
  }
def RawURCL(a, b):return a, b
def CleanURCL(a, b):return a, b