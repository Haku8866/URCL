CPU_stats = {
  "REGISTERS":"8",
  "MEMORY": "256",
  "DATABUS_WIDTH": "8",
  "RUN_RAM": True,
  "MANUAL_LABEL_REMOVAL": False,
  "SP_IS_REG": True,
  "SP_LOCATION": 255,
  "FLIPPED_STACK": False,
  "STACK_START": 0,
  "MANUAL_SP_REMOVAL": False,
  }
Instruction_table = {
    "ADD":   [True, ""],
    "SUB":   [True, ""],
    "RSH":   [True, ""],
    "LSH":   [True, ""],
    "INC":   [True, ""],
    "DEC":   [True, ""],
    "MOV":   [True, ""],
    "XOR":   [True, ""],
    "AND":   [True, ""],
    "OR":    [True, ""],
    "NOR":   [True, ""],
    "NAND":  [True, ""],
    "XNOR":  [True, ""],
    "NOT":   [True, ""],
    "IMM":   [True, ""], # <B> will be an immediate
    "LOD":   [True, ""],
    "STR":   [True, ""],
    "JMP":   [True, ""],
    "BRC":   [True, ""],
    "BNC":   [True, ""],
    "BRZ":   [True, ""],
    "BNZ":   [True, ""],
    "BRN":   [True, ""],
    "BRP":   [True, ""],
    "NOP":   [True, ""],
    "HLT":   [True, ""],
    "DW":    [True, ""], # Only for RUN RAM
    "IN":    [True, ""], # <B> will be an immediate (port)
    "OUT":   [True, ""], # <A> will be an immediate (port)
    }
from URCL import instruction
def RemoveLabels(code):
    return code
def getProgramLength(code):
    return 0
def RawURCL(code):
    return code
def CleanURCL(code, instructions):
    return code, instructions
def LabelISA(code):
    return code
def FinalISA(code):
    return code