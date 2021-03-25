import sys as s
import copy
end = (
    lambda ex, tag: input(f"\n--- Something went wrong :( ---\n\n{ex} {tag}\n")
    and s.exit()
)


class instruction:
    def __init__(self, label, opcode, operandList):
        self.label, self.opcode, self.operandList = label, opcode, operandList


labelCount, regUsage, ramUsage = 0, [], []

maxRes = 0
MINRAM = 0
MINREG = 0
BITS = ("", 0)
RUNRAM = False
IMPORTS = []
IMPORTED = []

operands = {
    "NEG": 2,
    "DW": 1,
    "DD": 1,
    "DQ": 1,
    "ADD": 3,
    "SUB": 3,
    "BSR": 3,
    "BSL": 3,
    "ADC": 3,
    "SBB": 3,
    "INC": 2,
    "DEC": 2,
    "MOV": 2,
    "IMM": 2,
    "XOR": 3,
    "AND": 3,
    "OR": 3,
    "NOR": 3,
    "NAND": 3,
    "XNOR": 3,
    "NOT": 2,
    "LOD": 2,
    "STR": 2,
    "JMP": 1,
    "BRC": 1,
    "BNC": 1,
    "BRZ": 1,
    "BNZ": 1,
    "BRN": 1,
    "BRP": 1,
    "BZR": 2,
    "BZN": 2,
    "NOP": 0,
    "HLT": 0,
    "MLT": 3,
    "DIV": 3,
    "MOD": 3,
    "SQRT": 2,
    "CAL": 1,
    "RET": 0,
    "PSH": 1,
    "POP": 1,
    "BRL": 3,
    "BRG": 3,
    "BRE": 3,
    "BNE": 3,
    "IN": 2,
    "OUT": 2,
    "BOD": 2,
    "BEV": 2,
    "RSH": 2,
    "LSH": 2,
    "CMP": 2,
    "SRS": 3,
    "BSS": 3,
    "BLE": 3,
    "BGE": 3,
    "BITS": 2,
    "MINREG": 1,
    "RUN": 1,
    "MINRAM": 1,
    "IMPORT": 0,
    "NAME": 1,
    "OPS": 1,
    "REG": 1,
    "IN": 1,
    "SETE": 3,
    "SETNE": 3,
    "SETG": 3,
    "SETL": 3,
    "SETGE": 3,
    "SETLE": 3,
}
JMPnching_ops = [
    "BRP",
    "BRN",
    "BNZ",
    "BRZ",
    "BNC",
    "BRC",
    "JMP",
    "BRL",
    "BRG",
    "BRE",
    "BNE",
    "BEV",
    "BOD",
    "BGE",
    "BLE",
    "BZR",
]

headers = [
    "RUN",
    "BITS",
    "MINRAM",
    "MINREG",
    "IMPORT"
]

cmplx_subs = {
    "SRS": [],
    "BSS": [],
    "MOD": [],
    "CAL": ["special"],
    "MLT": [
        instruction("", "PSH", ["<B>"]),
        instruction("", "IMM", ["<A>", "0"]),
        instruction("", "ADD", ["<A>", "<A>", "<C>"]),
        instruction("", "DEC", ["<B>", "<B>"]),
        instruction("", "BNZ", ["-2"]),
        instruction("", "POP", ["<B>"]),
    ],
    "DIV": [
        instruction("", "PSH", ["$3"]),
        instruction("", "PSH", ["$1"]),
        instruction("", "PSH", ["$2"]),
        instruction("", "MOV", ["$1", "<B>"]),
        instruction("", "MOV", ["$2", "<C>"]),
        instruction("", "IMM", ["$3", "0"]),
        instruction("", "SUB", ["$1", "$1", "$2"]),
        instruction("", "BRC", ["+3"]),
        instruction("", "INC", ["$3", "$3"]),
        instruction("", "JMP", ["-3"]),
        instruction("", "POP", ["$2"]),
        instruction("", "POP", ["$1"]),
        instruction("", "BNE", ["+4", "<A>", "$3"]),
        instruction("", "POP", ["$0"]),
        instruction("", "JMP", ["+3"]),
        instruction("", "MOV", ["<A>", "$3"]),
        instruction("", "POP", ["$3"]),
    ],
    "BRL": [
        instruction("", "SUB", ["$0", "<B>", "<C>"]),
        instruction("", "BNC", ["<A>"]),
    ],
    "BRG": [
        instruction("", "SUB", ["$0", "<C>", "<B>"]),
        instruction("", "BNC", ["<A>"]),
    ],
    "BRE": [
        instruction("", "CMP", ["<B>", "<C>"]),
        instruction("", "BRZ", ["<A>"]),
    ],
    "BNE": [
        instruction("", "CMP", ["<B>", "<C>"]),
        instruction("", "BNZ", ["<A>"]),
    ],
    "BSR": [
        instruction("", "PSH", ["$1"]),
        instruction("", "MOV", ["$1", "<C>"]),
        instruction("", "MOV", ["<A>", "<B>"]),
        instruction("", "RSH", ["<A>", "<A>"]),
        instruction("", "DEC", ["$1", "$1"]),
        instruction("", "BNZ", ["-2"]),
        instruction("", "POP", ["$1"]),
    ],
    "BSR": [
        instruction("", "PSH", ["$1"]),
        instruction("", "MOV", ["$1", "<C>"]),
        instruction("", "MOV", ["<A>", "<B>"]),
        instruction("", "RSH", ["<A>", "<A>"]),
        instruction("", "DEC", ["$1", "$1"]),
        instruction("", "BNZ", ["-2"]),
        instruction("", "POP", ["$1"]),
    ],
    "CMP": [
      instruction("", "SUB", ["$0", "<A>", "<B>"])
    ],
    "ADC": [
        instruction("", "BNC", ["+3"]),
        instruction("", "ADD", ["<A>", "<B>", "<C>"]),
        instruction("", "JMP", ["+3"]),
        instruction("", "ADD", ["<A>", "<B>", "<C>"]),
        instruction("", "INC", ["<A>", "<A>"]),
    ],
    "SBB": [
        instruction("", "BNC", ["+3"]),
        instruction("", "SUB", ["<A>", "<B>", "<C>"]),
        instruction("", "JMP", ["+3"]),
        instruction("", "SUB", ["<A>", "<B>", "<C>"]),
        instruction("", "DEC", ["<A>", "<A>"]),
    ],
    "SETE": [
      instruction("", "CMP", ["<B>", "<C>"]),
      instruction("", "BNZ", ["+2"]),
      instruction("", "IMM", ["<A>", "1"]),
    ],
    "SETNE": [
      instruction("", "CMP", ["<B>", "<C>"]),
      instruction("", "BRZ", ["+2"]),
      instruction("", "IMM", ["<A>", "1"]),
    ],
    "SETG": [
      instruction("", "CMP", ["<B>", "<C>"]),
      instruction("", "BRC", ["+2"]),
      instruction("", "IMM", ["<A>", "1"]),
    ],
    "SETL": [
      instruction("", "CMP", ["<B>", "<C>"]),
      instruction("", "BNC", ["+2"]),
      instruction("", "IMM", ["<A>", "1"]),
    ],
    "SETGE": [
      instruction("", "CMP", ["<B>", "<C>"]),
      instruction("", "BRC", ["+2"]),
      instruction("", "IMM", ["<A>", "1"]),
    ],
    "SETLE": [
      instruction("", "CMP", ["<C>", "<B>"]),
      instruction("", "BRC", ["+2"]),
      instruction("", "IMM", ["<A>", "1"]),
    ],
    "BOD": [
      instruction("", "PSH", ["$1"]),
      instruction("", "AND", ["$1", "<B>", "1"]),
      instruction("", "BNZ", ["+3", "$1"]),
      instruction("", "POP", ["$1"]),
      instruction("", "JMP", ["<A>"]),
      instruction("", "POP", ["$1"]),
    ],
    "BEV": [
      instruction("", "PSH", ["$1"]),
      instruction("", "AND", ["$1", "<B>", "1"]),
      instruction("", "BRZ", ["+3", "$1"]),
      instruction("", "POP", ["$1"]),
      instruction("", "JMP", ["<A>"]),
      instruction("", "POP", ["$1"]),
    ],
    "BLE": [
      instruction("", "CMP", ["<C>","<B>"]),
      instruction("", "BNC", ["<A>"])
    ],
    "BGE": [
      instruction("", "CMP", ["<B>","<C>"]),
      instruction("", "BNC", ["<A>"])
    ],
    "BZR": [
      instruction("", "ADD", ["<B>", "<B>", "$0"]),
      instruction("", "BRZ", ["<A>"])
    ],
    "NEG": [
      instruction("", "SUB", ["<A>", "$0", "<B>"])
    ]
}

def importProgram(name):
    try:
        return [line.strip() for line in open(name, "r", encoding="utf8")]
    except Exception as ex:
        end(
            ex,
            "- try checking:\n1. Is it in a different folder to URCL.py?\n2. Are you running URCL.py from elsewhere?\n 3. 'invalid syntax'? An error with the ISA designer's code.",
        )


def removeComments(program):
    for y in range(len(program)):
        line = program[y].rstrip("\n").split("//")[0].split(";")[0].strip().split(" ")
        if program[y].startswith("@"):
            line = [""]
        for x in range(len(line)):
            line[x] = line[x].strip()
            if len(line[x]) >= 2 and line[x][0] == "R" and line[x][1].isnumeric():
                line[x] = "$" + line[x][1:]
            line[x] = "".join(
                list(
                    filter(
                        lambda a: (
                            a in " _.-+=*<()>$#" or a.isnumeric() or a.isalpha()
                        ),
                        line[x],
                    )
                )
            )
        program[y] = " ".join(line)
    return list(filter(None, program))

def convertToInstructions(program):
    global RUNRAM
    global operands
    global labelCount
    code, label = [], ""
    for x in range(len(program)):
        operandList, line, operandCount, opcode = (
            [],
            program[x].split(),
            operands.get(program[x].split()[0], None),
            program[x].split()[0],
        )
        if line[0][0] == ".":
            label = " ".join(line)
        elif operandCount != None:
            operandList = line[1:]
            code.append(instruction(label, opcode, operandList))
            label = ""
        else:
            end(
                f"Unknown instruction '{line[0]}'",
                "- try checking:\n1. Is the file written in the lastest version of URCL?\n2. If so, has anyone raised this missing feature on the URCL discord yet? (https://discord.gg/jWRr2vx)",
            )
    return list(filter(None, code))


def fixLabels(program):
    global JMPnching_ops
    global labelCount
    try:
        for x in range(len(program)):
            if program[x].opcode in JMPnching_ops:
                address = program[x].operandList[0]
                if address[0] in "+-":
                    if program[x + int(address)].label == "":
                        (
                            program[x].operandList[0],
                            program[x + int(address)].label,
                            labelCount,
                        ) = (
                            f".label__{labelCount}__",
                            f".label__{labelCount}__",
                            labelCount + 1,
                        )
                    else:
                        program[x].operandList[0] = program[x + int(address)].label
        return program
    except Exception as ex:
        end(
            ex,
            "- try checking:\n1. Is there a bug in the URCL program, such as JMPnching past the end?\n2. If not, this may be an error with URCL.py, if you are sure it is, then please report it on the URCL discord. (https://discord.gg/jWRr2vx)",
        )


def replaceComplex(program):
    global labelCount
    for x in range(len(program)):
        ins, opcode, label, operandList = (
            program[x],
            program[x].opcode,
            program[x].label,
            program[x].operandList,
        )
        if len(ISA.Instruction_table.get(opcode, [1])) == 1 and cmplx_subs.get(opcode) != None:
            if opcode == "CAL":
                pop = "LOD"
                psh = "STR"
                swapped = False
                operandList = " ".join(operandList)
                if "$" in operandList:
                    labelName = operandList.split("(")[0] + str(len(operandList.split()))
                else:
                    labelName = operandList.split("(")[0]
                operands = operandList.split("(")[1][:-1]
                operands = operands.split()
                operands = [o.strip() for o in operands]
                for y in range(len(program)):
                    if f"{labelName}" in program[y].label:
                        funcLabelName = program[y].label
                        form = program[y].label.split("(")[1].split("#")[0]
                        regs = program[y].label.split("#")[1][:-1]
                        for z in range(y,len(program)):
                            if program[z].opcode == "RET":
                                #program[z].opcode = "JMP"
                                program[z].operandList.append(f"${int(regs)+1}")
                                break
                        break
                insert = []
                ret_before_name = 0
                if not ISA.CPU_stats["STR_OVER_PSH"]:
                    pop = "POP"
                    psh = "PSH"
                    swapped = True
                for y in range(x, len(program)):
                    if program[y].opcode == "RET":
                        ret_before_name = 1
                        break
                    elif "#" in program[y].label and "(" in program[y].label:
                        ret_before_name = 2
                        break
                if ret_before_name == 1:
                    ret_before_name = 0
                    for y in range(x, 0, -1):
                        if "#" in program[y].label and "(" in program[y].label:
                            ret_before_name = 1
                            break
                        elif program[y].opcode == "RET":
                            ret_before_name = 2
                            break
                    if ret_before_name == 1:
                        pop = "POP"
                        psh = "PSH"
                        swapped = True
                outs = form.count("o")
                for y in range(1, int(regs)+2):
                    if y == 1:l = program[x].label
                    else:l = ""
                    if f"${y}" in operands[:outs]:
                        pass
                    else:
                        insert.append(instruction(l, psh, [f"${y}"] if swapped else [f".RES_{y}", f"${y}"]))
                for y in range(0, len(operands)):
                    if form[y] == "i":
                        insert.append(instruction("", "MOV", [f"${y+1}", f"{operands[y]}"]))
                insert.append(instruction("", "IMM", [f"${int(regs)+1}", f".label__{labelCount}__"]))
                insert.append(instruction("", "JMP", [funcLabelName]))
                insert.append(instruction(f".label__{labelCount}__", pop, [f"${int(regs)+1}"] if swapped else [f"${int(regs)+1}", f".RES_{int(regs)+1}"]))
                labelCount += 1
                for y in range(int(regs),len(form),-1):
                    insert.append(instruction("",pop,[f"${z}"] if swapped else [f"${z}", f".RES_{z}"]))
                for y in range(0, len(form)):
                    if form[y] == "o":
                        insert.append(instruction("","MOV",[operands[y], f"${y+2}"]))
                outputs = []
                for z in range(len(form)):
                    if form[z] == "o":
                        outputs.append(operands[z][1:])
                form = form[::-1]
                for z in range(0, len(form)):
                    z = len(form)-z
                    if not (str(z) in outputs):
                        insert.append(instruction("",pop,[f"${z}"] if swapped else [f"${z}", f".RES_{z}"]))
                    #else:
                    #    if swapped:
                    #        insert.append(instruction("",pop,["$0"]))
                program = program[:x] + insert + program[x+1:]
                return False, program
            else:
                coreTranslation = copy.deepcopy(cmplx_subs[opcode])
                for i, instr in enumerate(coreTranslation):
                    if i == 0:
                        coreTranslation[0].label = label
                    for y in range(len(coreTranslation[i].operandList)):
                        for z in range(0, 26):
                            if f"<{chr(z+65)}>" in coreTranslation[i].operandList[y]:
                                coreTranslation[i].operandList[y] = operandList[z]
                program = program[:x] + coreTranslation + program[x + 1 :]
                return False, program
    return True, program

def optimise(program):
    done = False
    while not done:
        done = True
        for x,line in enumerate(program):
            if line.opcode == "MOV":
                if line.operandList[0] == line.operandList[1]:
                    program.pop(x)
                    done = False
                    break
            if line.opcode == "MOV":
                if line.operandList[1][0] != "$":
                    program[x].opcode = "IMM"
            if line.opcode == "IMM":
                if line.operandList[1][0] == "$":
                    program[x].opcode = "MOV"
            if line.opcode == "RET" and line.operandList != []:
                program[x].opcode = "JMP"
    return program

def fixImmediates(program):
    global JMPnching_ops
    for x, line in enumerate(program):
        if line.opcode not in JMPnching_ops and line.opcode != "CAL":
            for y, operand in enumerate(line.operandList):
                if operand[0] == "-":
                    program[x].operandList[y] = str(2**int(ISA.CPU_stats["DATABUS_WIDTH"])-int(operand[1:]))
                if operand[0] == "#" and operand[1:].isnumeric():
                    program[x].operandList[y] = program[x].operandList[y][1:]
                if operand[0] == "M" and operand[1:].isnumeric():
                    program[x].operandList[y] = program[x].operandList[y][1:]
                else:
                    # TODO: Bit patterns
                    # How to detect them?
                    # How to expand them?
                    pass
    return program


def convertToISA(program):
    ISAprogram = []
    for line in program:
        ISAsnippet = ISA.Instruction_table[line.opcode][1:].copy()
        for x in range(len(line.operandList)):
            if line.operandList[x][0] == ".":
                line.operandList[x] = "#__" + line.operandList[x]
        for x in range(len(ISAsnippet)):
            for z in range(0, 26):
                if f"<{chr(z+65)}>" in ISAsnippet[x]:
                    ISAsnippet[x] = ISAsnippet[x].replace(f"<{chr(z+65)}>", line.operandList[z])
        if line.label != "":
            ISAsnippet[0] = ISAsnippet[0] + f" %__{line.label}"
        ISAprogram += ISAsnippet
    return ISAprogram


def removeISALabels(program):
    for x in range(len(program)):
        if "%__." in program[x]:
            label, program[x] = program[x].split("%__")[1], program[x].split("%__")[0]
            for y in range(len(program)):
                program[y] = program[y].replace(f"#__{label}", f"{x}")
    return program

def readHeaders(program):
    global IMPORTS
    global BITS
    global RUNRAM
    global MINREG
    global MINRAM
    done = False
    while not done:
        for x, line in enumerate(program):
            if line.opcode == "BITS":
                BITS = (line.operandList[0], int(line.operandList[1]))
                if not eval(f"{ISA.CPU_stats['DATABUS_WIDTH']} {BITS[0]} {BITS[1]}"):
                    print(f"WARNING: this program is designed for a CPU with a databus width {BITS[0]} {BITS[1]}. (Target ISA is {ISA.CPU_stats['DATABUS_WIDTH']})")
                program.pop(x)
            elif line.opcode == "RUN":
                if ("RAM" == line.operandList[0]): 
                    RUNRAM = True
                if not (RUNRAM == ISA.CPU_stats["RUN_RAM"]):
                    print(f"WARNING: this program is designed for a CPU that runs from {line.operandList[0]}. (Target ISA runs from {ISA.CPU_stats['RUN_RAM']})")
                program.pop(x)
            elif line.opcode == "IMPORT":
                IMPORTS = line.operandList
                program.pop(x)
            elif line.opcode == "MINREG":
                MINREG = int(line.operandList[0])
                if MINREG > int(ISA.CPU_stats["REGISTERS"]):
                    print(f"WARNING: this program is designed for a CPU with {MINREG} registers. (Target ISA has {ISA.CPU_stats['REGISTERS']})")
                program.pop(x)
            elif line.opcode == "MINRAM":
                MINRAM = int(line.operandList[0])
                if MINRAM > int(ISA.CPU_stats["MEMORY"]):
                    print(f"WARNING: this program is designed for a CPU with {MINRAM} words of RAM. (Target ISA has {ISA.CPU_stats['MEMORY']})")
                program.pop(x)
            else:
                done = True
            break
    return program

def importLibs(program):
    global IMPORTED
    global IMPORTS
    done = False
    while not done:
        done = True
        for x, line in enumerate(program):
            if line.opcode == "CAL" and line.operandList[0][1:].split("_")[0] in IMPORTS:
                done = False
                libfile = open(f"lib_{line.operandList[0][1:].split('_')[0]}.urcl", "r")
                function = []
                copy = False
                for y, subline in enumerate(libfile):
                    if subline.split("//")[0].strip() == "":
                        continue
                    if subline.split()[0] == "NAME" and subline.split()[1] == line.operandList[0].split("_")[1].split("(")[0]:
                        copy = True
                        function.append(f"NAME {line.operandList[0][1:].split('(')[0]}")
                        continue
                    if copy:
                        if subline.split()[0] == "BITS" and not eval(f"{ISA.CPU_stats['DATABUS_WIDTH']} {subline.split()[1]} {subline.split()[2]}"):
                            copy = False
                            function = []
                            continue
                        elif subline.split()[0] == "RUN" and not (("RAM" == subline.split()[1]) == ISA.CPU_stats["RUN_RAM"]):
                            copy = False
                            function = []
                            continue
                        elif subline.split()[0] == "OPS" and not (len(line.operandList) == int(subline.split()[1])):
                            copy = False
                            function = []
                            continue
                        function.append(subline.strip())
                        if subline.split()[0] == "RET":
                            break
                libfile.close()
                function = removeComments(function)
                function = convertToInstructions(function)
                function = fixImmediates(function)
                function = fixLabels(function)
                match = False
                for x,item in enumerate(IMPORTED):
                    match = True
                    for y,ins in enumerate(IMPORTED[x]):
                        try:
                            if not (IMPORTED[x][y].opcode == function[y].opcode and IMPORTED[x][y].label == function[y].label and IMPORTED[x][y].operandList == function[y].operandList):
                                match = False
                                break
                        except:
                            match = False
                            break
                    if match:
                        break
                if not match:
                    program += function
                    IMPORTED.append(function)
                    break
                else:
                    done = True
    return program

def reduceLibs(program):
    for x, line in enumerate(program):
        if line.opcode == "NAME":
            lab = line.operandList[0]
            ops = 0
            inp = 0
            reg = 0
            nam = line.operandList[0]
            done = False
            while not done:
                for y, subline in enumerate(program[x:]):
                    if subline.opcode == "NAME":
                        program.pop(x+y)
                    elif subline.opcode == "RUN":
                        program.pop(x+y)
                    elif subline.opcode == "OPS":
                        ops = int(subline.operandList[0])
                        program.pop(x+y)
                    elif subline.opcode == "REG":
                        reg = int(subline.operandList[0])
                        program.pop(x+y)
                    elif subline.opcode == "IN":
                        inp = int(subline.operandList[0])
                        program.pop(x+y)
                    elif subline.opcode == "BITS":
                        program.pop(x+y)
                    else:
                        program[x+y].label = f".{lab}{ops}({'o'*(ops-inp)}{'i'*inp}#{reg})"
                        done = True
                    break
    return program

def allocateReservedRAM(program):
    global MINRAM
    global maxRes
    labels = []
    operandLists = []
    if RUNRAM:
        for line in program:
            labels.append(line.label)
            operandLists.append(line.operandList)
        for lst in operandLists:
            for item in lst:
                if item[:5] == ".RES_" and item not in labels:
                    if int(item[5:]) > maxRes:
                        maxRes = int(item[5:])
                    program.append(instruction(item,"DW",["0"]))
                    labels.append(item)
    else:
        for x, line in enumerate(program):
            for y, operand in enumerate(program[x].operandList):
                if operand[:5] == ".RES_":
                    if int(item[5:]) > maxRes:
                        maxRes = int(item[5:])
                    program[x].operandList[y] = f"#{MINRAM+int(operand[5:])}"
    return program

def regSubstitution(program):
    global maxRes
    blocked = ["IMM", "LOD", "CAL"]
    done = False
    while not done:
        done = True
        for x, line in enumerate(program):
            label = line.label
            if ISA.Instruction_table[line.opcode][0] and line.opcode not in blocked:
                offenders = []
                for y, operand in enumerate(line.operandList):
                    if operand[0] != "$" and operand[0] not in offenders and y > 0:
                        offenders.append(operand)
                if len(offenders) == 0:
                    continue
                program[x].label = ""
                insert = []
                originalMaxRes = maxRes
                for y,offender in enumerate(offenders):
                    insert.append(instruction(label, "STR", [f".RES_{maxRes+y+1}", f"${y+1}"]))
                    insert.append(instruction("", "IMM", [f"${y+1}", offender]))
                    for z, item in enumerate(line.operandList):
                        if offender == item:
                            program[x].operandList[z] = f"${y+1}"
                    maxRes += 1
                    label = ""
                insert.append(program[x])
                for y,offender in enumerate(offenders):
                    if f"${y+1}" != line.operandList[0] or (f"${y+1}" != line.operandList[0] and operands[line.opcode] > 1):
                        insert.append(instruction("", "LOD", [f"${y+1}", f".RES_{originalMaxRes+y+1}"]))
                program = program[:x] + insert + program[x+1:]
                done = False
                break
    return program

def fixStackPointer(program):
    # TODO: The stack pointer is either a register
    #       or in memory. Find out which and put it in
    #       an unused register somehow.
    return program

def main():
    global operands
    global RUNRAM
    program, done = importProgram(input("File to compile? (with extension) ")), False
    program = removeComments(program)
    program = convertToInstructions(program)
    try:
        program = ISA.RawURCL(program)
    except Exception as ex: 
        end(ex,"- no suggestions, problem with ISA designer's raw URCL tweaks. Report this to them if necessary.")
    program = fixImmediates(program)
    program = fixLabels(program)
    program = readHeaders(program)
    program = importLibs(program)
    program = reduceLibs(program)
    while not done:
        done, program = replaceComplex(program)
        program = allocateReservedRAM(program)
        program = fixLabels(program)
    try: program = ISA.CleanURCL(program)
    except Exception as ex:end(ex,"- no suggestions, problem with ISA designer's clean URCL tweaks. Report this to them if necessary.",)
    program = optimise(program)
    program = fixImmediates(program)
    program = regSubstitution(program)
    program = allocateReservedRAM(program)
    program = fixStackPointer(program)
    [print(f"\nURCL code:\n{ins.label:>25} {ins.opcode:<7} {', '.join(ins.operandList)}") if x == 0 else print(f"{ins.label:>25} {ins.opcode:<7} {', '.join(ins.operandList)}")for x, ins in enumerate(program)]
    try:program = convertToISA(program)
    except Exception as ex:end(ex,"- try checking:\n1. Are all the instructions correctly implemented in the ISA's config file? (It is likely that a basic instruction is missing)\n2. Is there a bug in the URCL program, such as JMPnching past the end?",)
    try:program = ISA.LabelISA(program)
    except Exception as ex:end(ex,"- no suggestions, problem with ISA designer's labelled ISA tweaks. Report this to them if necessary.",)
    if not ISA.CPU_stats["MANUAL_LABEL_REMOVAL"]:program = removeISALabels(program)
    else:program = ISA.RemoveLabels(program)
    if ISA.CPU_stats["LINENUMS"]:program = [(str(x).zfill(3) + ": " + line) for x, line in enumerate(program)]
    try:program = ISA.FinalISA(program)
    except Exception as ex:end(ex,"- no suggestions, problem with ISA designer's final ISA tweaks. Report this to them if necessary.",)
    [print(f"\n{ISA.__name__} code:\n{line}") if x == 0 else print(line) for x, line in enumerate(program)]


if __name__ == "__main__":
    try:
        exec(f"import {input('Compile to which ISA? (without extension) ')} as ISA")
    except Exception as ex:end(ex,"- try checking:\n1. Is it in a different folder to URCL.py?\n2. Are you running URCL.py from elsewhere?",)
    main()
