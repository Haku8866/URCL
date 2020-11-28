#URCL_documentation: https://docs.google.com/spreadsheets/d/14u15VlSYORlt8EQu3C0ow0LTppoeio9gm2_z0Q4bOD8/edit?usp=sharing

CPU_stats = {
    "REGISTERS":"1024",
    "MEMORY": "1024",
    "LINENUMS": False,
    "DATABUS_WIDTH":"8",
    }

Instruction_table = {
    "----BASIC----": "These are basic instructions, you should aim to fill in all of these as they will be used frequently in programs. The compiler may crash if certain instructions are missing.",
    
    # 3 operand instructions, must contain <A> <B> and <C> where <A> is the destination and <B> and <C> are sources (where applicable).
    "ADD":   ["LDA <B>","LDA <C>","ADD","STORE <A>"],
    "SUB":   [],
    "XOR":   [],
    "AND":   [],
    "OR":    [],
    "NOR":   [],
    "NAND":  [],
    "XNOR":  [],

    # 2 operand instructions, must contain <A> and <B> where <A> is the destination and <B> is the source (where applicable).
    "INC":   ["INC <B>", "STORE <A>"],
    "DEC":   [],
    "IMM":   ["<A> = <B>"],
    "RSH":   [],
    "LSH":   [],
    "NOT":   [],
    "MOV":   [],
    "LOAD":  [],
    "STORE": [],
    
    # 1 operand instructions, must contain <A>.
    "BRA":   ["JMP <A>"],
    "BRC":   [],
    "BNC":   ["JMC +2","JMP <A>"],
    "BRZ":   [],
    "BNZ":   [],
    "BRN":   [],
    "BRP":   [],

    # 0 operand instructions.
    "HLT":   ["HLT"],
    "NOP":   [],

    "----COMPLEX----": "These are complex instructions. You may wish to use the pre-written subroutines for these using only the core instructions by leaving them blank.",
    
    # 3 operand instructions, must contain <A> <B> and <C> where <A> is the destination and <B> and <C> are sources (where applicable).
    "MLT":   [],
    "DIV":   [],
    "MOD":   [],
    "ADC":   [],
    "SBB":   [],
    "BSR":   [],
    "BSL":   [],
    "SRS":   [],
    "BSS":   [],
    "BRL":   [],
    "BRG":   [],
    "BRE":   [],
    "BNE":   [],
    "BLE":   [],
    "BGE":   [],
    "SETE":  [],
    "SETNE": [],
    "SETG":  [],
    "SETL":  [],
    "SETGE": [],
    "SETLE": [],

    # 2 operand instructions, must contain <A> and <B> where <A> is the destination and <B> is the source (where applicable).
    "BOD":   [],
    "BEV":   [],
    "IN":    [],
    "OUT":   [],
    "CMP":   [],

    # 1 operand instructions, must contain <A>.
    "CAL":   [],
    "PSH":   [],
    "POP":   [],

    # 0 operand instructions.
    "RET":   [],
    }

def RawURCL(code):
    for x in range(0, len(code)):
        pass
    return code

def CleanURCL(code):
    for x in range(0, len(code)): # Please note that "cleaned" URCL is different from normal URCL syntax.
        pass                      # This is what you will see in the "URCL code:" output from the program.
    return code

def LabelISA(code):
    for x in range(0, len(code)):
        pass
    return code

def FinalISA(code):
    for x in range(0, len(code)):
        opcode = code[x][0]     # Showing how you can split up the instruction. (If you have the LINENUMS option set to True, then code[x][0] will be the line number)
        if len(code[x]) > 1:
            operands = code[x][1:]
            for operand in operands:
                if operand[0] == "$":
                    operand = "£" + operand[1:] # In this example ISA, registers are denoted with a £ sign instead of a $ sign.
    return code