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
    "IMM":   [False, ""], # IMM cannot accept a register
    "LOD":   [False, ""], # LOD cannot accept a register
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
    "IN":    [False, ""], # IN cannot accept a register
    "OUT":   [True, ""],
    }
from URCL import instruction
def RemoveLabels(code):
    return code
def getProgramLength(code):
    return 0
def RawURCL(code):
    return code
def CleanURCL(code):
    return code
def LabelISA(code):
    return code
def FinalISA(code):
    return code