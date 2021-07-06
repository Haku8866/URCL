#URCL_documentation: https://docs.google.com/spreadsheets/d/14u15VlSYORlt8EQu3C0ow0LTppoeio9gm2_z0Q4bOD8/edit?usp=sharing

CPU_stats = {
  # General information

  # Number of general purpose registers that the compiler can use. R0, the PC, MAR, etc. are not included in this.
  "REGISTERS": "4",              
  # Number of available memory locations
  "MEMORY": "256",               
  # Size of a data word
  "DATABUS_WIDTH": "8",          
  # False if your CPU runs from ROM
  "RUN_RAM": True,
  # Whether or not labels should be replaced with absolute addresses.
  # If you use RUN RAM and multi-word instructions, or variable length instructions, set this to False and remove labels yourself.
  "REMOVE_LABELS": True,  # Whether or not memory addresses (#) should be shifted to avoid collisions with the program.
  # If you use RUN ROM, this does not apply.
  # If you use RUN RAM and multi-word instructions, variable length instructions, or non-URCL-like syntax, set this to False and adjust the addresses yourself.
  "SHIFT_RAM": True,

  # Stack information

  # Which reg should the SP be stored in? (0 means choose automatically, the highest available  GPR value is recommended for this)
  "SP_LOCATION": "0",
  # Is the SP included in the GPRs mentioned above?
  "SP_IS_GPR": True,  # Does the stack grow upwards instead of downwards? AKA should PSH be changed to "INC SP, SP..." instead of the usual "DEC SP, SP..."?
  "REVERSED_STACK": False,
  # What should the stack pointer's initial value be? For a non-reversed stack, 0 means "start from the highest memory address" as 0 - 1 = -1 = 0b1111...
  "SP_VALUE": "0",
  # Should the stack pointer be left as "SP" in the final code? (So you can swap it out yourself)
  "KEEP_SP": False,

  # Notes:
  # If you pick a low GPR for your SP (IE R1 or R2) programs are likely to use it, which would be annoying, so it is strongly recommended that you choose the highest value available.
  # The SP cannot be stored in memory because this has detrimental effects on performance.
  # If you have a hardware stack, write specific ISA translations for PSH and POP to handle it.
  }

Instruction_table = {
    # This is where you should provide translations for URCL instructions, you should aim to fill in as many as you can.
    # Strictly speaking only the "core" section is necessary, BUT, programs will become huge and inefficient if you only support the core instructions.
    # In general, the more translations you provide the smoother and more efficient the translation from URCL -> your ISA will be.
    # For all of these instructions, <A>, <B>, and <C> are registers unless a comment explicitly specifies otherwise. (Eg. for IMM, IN, and OUT)
    
    # OPTIONAL: (everything still works without this)
    # If you would like to provide a translation for instructions where the immediates aren't all registers, you can add variants to the list.
    # SUB has been used for this example. You can see that SUB has 4 different translations available:
    # "SUB" - all registers,   e.g. SUB $1, $2, $3
    # "SUB_rri" - reg reg imm, e.g. SUB $1, $2, 15
    # "SUB_rir" - reg imm reg, e.g. SUB $1, 30, $2
    # "SUB_rii" - reg imm imm, e.g. SUB $1, 30, 15
    # This can be done for any instruction, you just need to provide the operand structure by appending "_xxx" to the opcode.
    # r = register
    # i = immediate (number)

    "ADD":   ["MOV <A>, <B>", "ADD <A>, <C>"],

    "SUB":     ["MOV <A>, <B>", "SUB <A>, <C>"],
    # Optional variations with different operand structures for extra performance
    "SUB_rri": ["IMM <C>", "MOV <A>, <B>", "SUB <A>, MDR"],
    "SUB_rir": ["IMM <B>", "MOV <A>, MDR", "SUB <A>, <C>"],
    "SUB_rii": ["MOV <A>, $0", "IMM <B>", "ADD <A>, MDR", "IMM <C>", "ADD <A>, MDR"],

    "RSH":   ["MOV <A>, <B>","RSH <A>"],
    "INC":   ["MOV <A>, <B>","INC <A>"],
    "DEC":   ["MOV <A>, <B>","DEC <A>"],
    "MOV":   ["MOV <A>, <B>"],
    "AND":   ["AND <A>, <B>"],
    "NOR":   ["ORE <A>, <B>", "NOT <A>"],
    "IMM":   ["IMM <B>", "MOV <A>, MDR"], # <B> will be an immediate (number)
    "LOD":   ["LDA <B>", "MOV <A>, MDR"],
    "STR":   ["MOV MDR, <B>", "STR <A>"],
    "JMP":   ["JMP <A>"],
    "BRZ":   ["JMP <A> if <B> == $0"],
    "NOP":   ["NOP"],
    "HLT":   ["HLT"],
    "BGE":   ["JMP <A> if <B> >= <C>"],
    "IN":    ["IN <A>, <B>"], # <B> will be an immediate (port, aka number)
    "OUT":   ["OUT <A>, <B>"], # <A> will be an immediate (port, aka number)
    "DW":    ["DW <A>"], # Only for RUN RAM, <A> will be an immediate (number)

    # Don't feel restricted to just this list though, you can provide translations for any instructions you like:
    "INS":   ["ISA line #1", "ISA line #2", "ISA line #3", "ISA line #4..."]
    }

Port_table = {
    # This is where you link URCL ports to ports on your CPU.
    # Any instances of "OUT %NUMB, $1" would be replaced with "OUT 0, $1" here, for example.
    "%NUMB": 0,
    "%INT": 0,
    "%TEXT": 1,
    "%ASCII": 1,
    # You can add more ports if you like, or even assign multiple URCL ports to the same ISA ports, as shown here.
}

from URCL import instruction, opcode, operand

# This is raw URCL, before labels and complex instructions are sorted out.
# i is the index of the instruction in the URCL code, ins is the actual instruction object.
# Here I am just extracting the instruction information as an example:
def RawURCL(code, opcodes):
    for i, ins in enumerate(code):
        # Label structure, ins.label is a list of labels.
        label = ins.label
        for lbl in label:
            lbl.type = lbl.type
            lbl.value = lbl.value
            pass
        # Opcode structure.
        opcode = ins.opcode
        opcode.name = opcode.name
        opcode.type = opcode.type
        opcode.complexity = opcode.complexity
        # Operand structure.
        operandList = ins.operandList
        for opr in operandList:
            opr.type = opr.type
            # Operand types:
            # - register (int)
            # - stackPtr (int)
            # - memAddr  (int)
            # - label    (str)
            # - number   (int)
            # Prefixes are not included.
            opr.value = opr.value
    return code, opcodes

# Clean URCL, all branches are now labels. Safe to add and remove instructions.
def CleanURCL(code, opcodes):
    return code, opcodes

# This is your ISA code with labels, there are no relative branches so you can add new ISA instructions in here.
# This code uses ISAinstruction objects. This is essentially just so that I can keep track of labels.
def LabelISA(code):
    for i, ins in enumerate(code):
        # Label is a list of labels in string form, with "." prefixes.
        label = ins.label
        # Instruction is the rest of the instruction.
        instruction = ins.instruction
    return code

# This is the final product, nothing is processed between this function being called and the code being printed to the console.
# If you have "REMOVE_LABELS" set to True, then you can't add or remove instructions here as absolute addresses will be used for branches.
# However, finishing touches such as removing any "$" signs for registers can still be done:
def FinalISA(code):
    for i, ins in enumerate(code):
        code[i].instruction = "".join(list(filter(lambda a: a != "$", code[i].instruction)))
    return code