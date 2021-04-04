CPU_stats = {
  "REGISTERS":"",
  "MEMORY": "",
  "DATABUS_WIDTH": "",
  "RUN_RAM": False,
  "LINENUMS": False,
  "MANUAL_LABEL_REMOVAL": False,
  "STR_OVER_PSH": False,
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
    "PSH":   [True, ""],
    "POP":   [True, ""],
    "IN":    [False, ""], # IN cannot accept a register
    "OUT":   [True, ""],
    }
from URCL import instruction
def RemoveLabels(code):
    return code
def RawURCL(code):
    for i, ins in enumerate(code):
    return code
def CleanURCL(code):
    return code
def LabelISA(code):
    for i, ins in enumerate(code):
        pass
    return code
def FinalISA(code):
    for i, ins in enumerate(code):
        pass
    return code