#URCL_documentation: https://docs.google.com/spreadsheets/d/14u15VlSYORlt8EQu3C0ow0LTppoeio9gm2_z0Q4bOD8/edit?usp=sharing

CPU_stats = {
  "REGISTERS":"4",               # Number of general purpose registers
  "MEMORY": "256",               # Number of available memory locations
  "DATABUS_WIDTH": "8",          # Size of a data word
  "RUN_RAM": True,               # False if your CPU runs from ROM
  "LINENUMS": False,             # True if you need line numbers prepended to each line of the output
  "MANUAL_LABEL_REMOVAL": False, # True if you need to handle labels yourself
  "STR_OVER_PSH": True,          # True if it's easier to use STR and LOD than PSH and POP
    }

Instruction_table = {
    # These are basic instructions, you should aim to fill in all of these as they will be used frequently in programs. 
    # The compiler may crash if certain instructions are missing.
    # You should fill these in assuming all parameters are registers, if you want to handle different cases involving immediates with code, then set the flag at the start to "False"
    "ADD":   [True, "MOV <A>, <B>", "ADD <A>, <C>"],
    "SUB":   [True, "MOV <A>, <B>", "SUB <A>, <C>"],
    "RSH":   [True, "MOV <A>, <B>","RSH <A>"],
    "LSH":   [True, "ADD <A>, <A>"],
    "INC":   [True, "MOV <A>, <B>","INC <A>"],
    "DEC":   [True, "MOV <A>, <B>","DEC <A>"],
    "MOV":   [True, "MOV <A>, <B>"],
    "XOR":   [True, "XOR <A>, <B>"],
    "AND":   [True, "AND <A>, <B>"],
    "OR":    [True, "ORE <A>, <B>"],
    "NOR":   [True, "ORE <A>, <B>", "NOT <A>"],
    "NAND":  [True, "AND <A>, <B>", "NOT <A>"],
    "XNOR":  [True, "XOR <A>, <B>", "NOT <A>"],
    "NOT":   [True, "NOT <A>"],
    "IMM":   [False, "IMM <B>", "MOV <A>, MDR"], # IMM cannot accept a register
    "LOD":   [False, "LDA <B>", "MOV <A>, MDR"], # LOD cannot accept a register
    "STR":   [True, "MOV MDR, <B>", "STR <A>"],
    "JMP":   [True, "JMP <A>"],
    "BRC":   [True, "JMP <A> if C"],
    "BNC":   [True, "JMP <A> if NC"],
    "BRZ":   [True, "JMP <A> if Z"],
    "BNZ":   [True, "JMP <A> if NZ"],
    "BRN":   [True, "MOV MDR, <B>", "ADD MDR, MDR", "JMP <A> if C"],
    "BRP":   [True, "MOV MDR, <B>", "ADD MDR, MDR", "JMP <A> if NC"],
    "NOP":   [True, "NOP"],
    "HLT":   [True, "HLT"],
    "DW":    [True, "DW <A>"],

    #These are complex instructions. You may wish to use the pre-written subroutines for these using only the core instructions.
    # PSH and POP are very important and don't have core translations yet.
    "PSH":   [True, "LDA .stack_ptr", "STR .next+1", "MOV MDR, <A>", ".next", "STR 0", "LDA .stack_ptr", "INC MDR", "STR .stack_ptr"],
    "POP":   [True, "LDA .stack_ptr", "DEC MDR", "STR .stack_ptr","LDA .stack_ptr", "STR .next+1", ".next", "LDA 0", "MOV <A>, MDR"],
    
    "IN":    [False, "IN <A>, <B>"], # IN cannot accept a register
    "OUT":   [True, "OUT <A>, <B>"],

    "COMPLEX_INS":   [True, "ISA line #1", "ISA line #2", "ISA line #3", "ISA line #4..."]
    }

from URCL import instruction

# This is the default label removal code. (It will not be called, it is here for demonstration)
def removeISALabels(program):
  for x in range(len(program)):
    if "%__." in program[x]:
      label, program[x] = program[x].split("%__")[1], program[x].split("%__")[0]
      for y in range(len(program)):
        program[y] = program[y].replace(f"#__{label}", f"{x}")
  return program

# If it is not suitable for your CPU, you can modify it as you wish or write your own:
def RemoveLabels(code):
    return code

def RawURCL(code):                      # This is raw URCL, before labels and complex instructions are sorted out.
    for i, ins in enumerate(code):      # i is the index of the instruction in the URCL code, ins is the actual instruction object.
        label = ins.label               # Obtaining information about the instruction
        opcode = ins.opcode
        operandList = ins.operandList
    return code

def CleanURCL(code):                  # Clean URCL, all branches are now labels. Safe to add and remove instructions.
    return code

def LabelISA(code):                   # This is your ISA code with labels, there are no relative branches so you can add new ISA instructions in here.
    for i, ins in enumerate(code):    # These do not use instruction objects, instead, strings are used. You can use list = str.split() and str = " ".join(list) to manipulate code.
        pass                          # Please be aware that some lines may have "%__.label" on the end, you should make your edits with this in mind.
    return code                       # Lines using labels as operands will use "#__.label" instead of just ".label".

def FinalISA(code):                   # This is the final product, nothing is processed between this function being called and the code being printed to the console.
    for i, ins in enumerate(code):    # Remember that only absolute addresses are used here, you may need to adjust line numbers or tweak values.
        pass                          # Inserting new instructions here will most likely break the code, as it will shift lines and make branches point to the wrong places.
    return code