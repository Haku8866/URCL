CPU_stats = {
  "REGISTERS":"7",
  "MEMORY": "256",
  "DATABUS_WIDTH": "8",
  "RUN_RAM": True,
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
  "SUB":  [1],
  "RSH":  [1],
  "LSH":  [1],
  "INC":  [1],
  "DEC":  [1],
  "MOV":  [1],
  "XOR":  [1],
  "AND":  [1],
  "OR":   [1],
  "NOR":  [1],
  "NAND": [1],
  "XNOR": [1],
  "NOT":  [1],
  "IMM":  [1], # <B> will be an immediate
  "LOD":  [1],
  "STR":  [1],
  "JMP":  [1],
  "BRZ":  [1],
  "BNZ":  [1],
  "BGE":  [1],
  "HLT":  [1],
  "DW":   [1], # Only for RUN RAM
  "IN":   [1], # <B> will be an immediate (port)
  "OUT":  [1], # <A> will be an immediate (port)
  }
def RawURCL(a, b):return a, b
def CleanURCL(a, b):return a, b