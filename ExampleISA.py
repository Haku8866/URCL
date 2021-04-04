#URCL_documentation: https://docs.google.com/spreadsheets/d/14u15VlSYORlt8EQu3C0ow0LTppoeio9gm2_z0Q4bOD8/edit?usp=sharing

CPU_stats = {
  "REGISTERS":"4",               # Number of general purpose registers
  "MEMORY": "256",               # Number of available memory locations
  "DATABUS_WIDTH": "8",          # Size of a data word
  "RUN_RAM": True,               # False if your CPU runs from ROM
  "LINENUMS": False,             # True if you need line numbers prepended to each line of the output
  "MANUAL_LABEL_REMOVAL": True,  # True if you need to handle labels yourself
  "STR_OVER_PSH": True,          # True if it's easier to use STR and LOD than PSH and POP
    }

Instruction_table = {
    # These are basic instructions, you should aim to fill in all of these as they will be used frequently in programs. 
    # The compiler may crash if certain instructions are missing.
    # You should fill these in assuming all parameters are registers, if you want to handle different cases involving immediates with code, then set the flag at the start to "False"
    # To act as an example, ADD has been set to False here to show how you would "manually handle an instruction"
    "ADD":   [False, "MOV <A>, <B>", "ADD <A>, <C>"],
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
    "DW":    [True, "DW <A>"], # Only for RUN RAM

    #These are important complex instructions. You may wish to use the pre-written subroutines for these using only the core instructions.
    # PSH and POP are very important and don't have core translations yet.
    "PSH":   [True, "LDA .stack_ptr", "STR .next+1", "MOV MDR, <A>", ".next", "STR 0", "LDA .stack_ptr", "INC MDR", "STR .stack_ptr"],
    "POP":   [True, "LDA .stack_ptr", "DEC MDR", "STR .stack_ptr","LDA .stack_ptr", "STR .next+1", ".next", "LDA 0", "MOV <A>, MDR"],  
    "IN":    [False, "IN <A>, <B>"], # IN cannot accept a register
    "OUT":   [True, "OUT <A>, <B>"],

    # You can support extra complex instructions natively if you would like to make the resulting ISA code more efficient.
    # Note that the special CAL instruction will always be handled by the compiler.
    "COMPLEX_INS":   [True, "ISA line #1", "ISA line #2", "ISA line #3", "ISA line #4..."]
    }

from URCL import instruction

# This is the default label removal code. (It will not be called, it is here for reference)
def removeISALabels(program):
  for x in range(len(program)):
    if "%__." in program[x]:                                                     # This checks to see if the line of ISA code has a label on the end
      label, program[x] = program[x].split("%__")[1], program[x].split("%__")[0] # If it does, remove it.
      for y in range(len(program)):
        program[y] = program[y].replace(f"#__{label}", f"{x}")                   # And then replace all instances of it with the address of where it was defined.
  return program

# For this ExampleISA, some instructions are longer than others.
def RemoveLabels(code):
    byteCount = 0
    byteList = []
    # To handle this, we can count the bytes for each instruction to tell us where in RAM each instruction will be stored.
    for x in range(len(code)):
        if code[x].split()[0] in ["LSH", "RSH"]:
            # For this example, RSH and LSH will be 2 bytes long instead of 1.
            byteList.append(byteCount)
            byteCount += 2
        elif code[x][0] != ".":
            # Anything else that isn't a label is 1 byte long.
            byteList.append(byteCount)
            byteCount += 1
        else:
            byteList.append(byteCount)
    # proceed as normal, just like the default code, except we use our special byteList instead of the raw line number.
    for x in range(len(code)):
        if "%__." in code[x]:
            label, code[x] = code[x].split("%__")[1], code[x].split("%__")[0]
            for y in range(len(code)):
                code[y] = code[y].replace(f"#__{label}", f"{byteList[x]}")
    return code

# This is raw URCL, before labels and complex instructions are sorted out.
# i is the index of the instruction in the URCL code, ins is the actual instruction object.
# Here I am just extracting the instruction information as an example:
def RawURCL(code):
    for i, ins in enumerate(code):
        label = ins.label
        opcode = ins.opcode
        operandList = ins.operandList
    return code

# Clean URCL, all branches are now labels. Safe to add and remove instructions.
# For example, you might want to trim any NOPs:
def CleanURCL(code):
    done = False
    while not done:
        done = True
        for i, ins in enumerate(code):
            label = ins.label
            opcode = ins.opcode
            operandList = ins.operandList
            if opcode == "NOP":
                code.pop(i)  # After changing the length of the list, it's a good idea to go back to the beginning and iterate through again.
                done = False # Iterating through the list as it changes length is a bad idea.
                break
    return code

# This is your ISA code with labels, there are no relative branches so you can add new ISA instructions in here.
# These do not use instruction objects, instead, strings are used. You can use list = str.split() and str = " ".join(list) to manipulate code.
# Please be aware that some lines may have "%__.label" on the end, you should make your edits with this in mind.
# Lines using labels as operands will use "#__.label" instead of just ".label".
def LabelISA(code):
    done = False
    while not done:
        done = True
        for i, ins in enumerate(code):
            # Here, only "ADD reg reg reg" is supported, so we need to handle "ADD reg IMM reg"
            # ins.split()[0] is the first word in the line, in this case, it's the opcode.
            if ins.split()[0] == "MOV":
                # if the first character of the second operand is a number, aka, check if the instruction is moving a register to a register or an immediate to a register.
                if ins.split()[2][0].isnumeric():
                    # MOV $1, 15 is not a valid MOV instruction, it should be IMM $1, 15. This fixes it.
                    code[i] = code[i].replace("MOV", "IMM")
            # Now, "ADD reg reg reg" and "ADD reg imm reg" are handled, but we need to handle "ADD reg imm/reg imm" as well.
            if ins.split()[0] == "ADD":
                if ins.split()[2][0].isnumeric():
                    # If this code triggers, we're dealing with ADD $1, 15.
                    # So, we need to change it to IMM 15 ; ADD $1, MDR.
                    code = code[0:i] + [f"IMM {ins.split()[2]}"] + [f"ADD {ins.split()[1]} MDR"] + code[i+1:]
                    done = False
                    # As before, if we're changing the length of the list, we need to break and iterate through from the start again.
                    break
    # Note that usually the compiler will handle all of this for you, this is only for if you have a special instruction such as "ADI: Add immediate"
    return code

# This is the final product, nothing is processed between this function being called and the code being printed to the console.
# Remember that only absolute addresses are used here, you may need to adjust line numbers or tweak values.
# Inserting new instructions here will most likely break the code, as it will shift lines and make branches point to the wrong places.
# However, finishing touches such as removing any "$" signs for registers can still be done:
def FinalISA(code):
    for i, ins in enumerate(code):
        code[i] = "".join(list(filter(lambda a: a != "$", code[i])))
    return code