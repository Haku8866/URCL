import sys as s
import os
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
SPreg = 0
fixSP = True
spisreg = True
usestacknotreg = False
temp = 0
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
    "PSH": ["special"],
    "POP": ["special"],
    "MLT": [
        instruction("", "PSH", ["<B>"]),
        instruction("", "IMM", ["<A>", "0"]),
        instruction("", "BNZ", ["+3"]),
        instruction("", "ADD", ["<A>", "<A>", "<C>"]),
        instruction("", "DEC", ["<B>", "<B>"]),
        instruction("", "JMP", ["-3"]),
        instruction("", "POP", ["<B>"]),
    ],
    "DIV": [
        instruction("", "PSH", ["<B>"]),
        instruction("", "IMM", ["<A>", "0"]),
        instruction("", "SUB", ["<B>", "<B>", "<C>"]),
        instruction("", "BRC", ["+3"]),
        instruction("", "INC", ["<A>", "<A>"]),
        instruction("", "JMP", ["-3"]),
        instruction("", "POP", ["<B>"]),
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
        instruction("", "PSH", ["<C>"]),
        instruction("", "MOV", ["<A>", "<B>"]),
        instruction("", "RSH", ["<A>", "<A>"]),
        instruction("", "DEC", ["<C>", "<C>"]),
        instruction("", "BNZ", ["-2"]),
        instruction("", "POP", ["<C>"]),
    ],
    "BSR": [
        instruction("", "PSH", ["<C>"]),
        instruction("", "MOV", ["<A>", "<B>"]),
        instruction("", "RSH", ["<A>", "<A>"]),
        instruction("", "DEC", ["<C>", "<C>"]),
        instruction("", "BNZ", ["-2"]),
        instruction("", "POP", ["<C>"]),
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
      instruction("", "PSH", ["<B>"]),
      instruction("", "AND", ["<B>", "<B>", "1"]),
      instruction("", "BRZ", ["+3"]),
      instruction("", "POP", ["<B>"]),
      instruction("", "JMP", ["<A>"]),
      instruction("", "POP", ["<B>"]),
    ],
    "BEV": [
      instruction("", "PSH", ["<B>"]),
      instruction("", "AND", ["<B>", "<B>", "1"]),
      instruction("", "BNZ", ["+3"]),
      instruction("", "POP", ["<B>"]),
      instruction("", "JMP", ["<A>"]),
      instruction("", "POP", ["<B>"]),
    ],
    "BLE": [
      instruction("", "CMP", ["<C>","<B>"]),
      instruction("", "BNC", ["<A>"])
    ],
    "BGE": [
      instruction("", "CMP", ["<B>","<C>"]),
      instruction("", "BRC", ["<A>"])
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
            if len(line[x]) >= 2 and line[x][0] == "M" and line[x][1].isnumeric():
                line[x] = "#" + line[x][1:]
            line[x] = "".join(
                list(
                    filter(
                        lambda a: (
                            a in " _.-+=*<()>$#&" or a.isnumeric() or a.isalpha()
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
    global temp
    for x in range(len(program)):
        ins, opcode, label, operandList = (
            program[x],
            program[x].opcode,
            program[x].label,
            program[x].operandList,
        )
        if ISA.Instruction_table.get(opcode) == None and cmplx_subs.get(opcode) != None:
            if opcode == "CAL":
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
                        regs = int(program[y].label.split("#")[1][:-1])
                ret_addr = f".label__{labelCount}__"
                labelCount += 1
                insert = [instruction(program[x].label, "PSH", [ret_addr])]
                for y,operand in enumerate(operands):
                    if form[y] == "i":
                        insert.append(instruction("", "PSH", [operand]))
                insert.append(instruction("", "JMP", [funcLabelName]))
                index = len(insert)
                for y in range(form.count("o")):
                    insert.append(instruction("", "POP", [f"${form.count('o')-y}"]))
                insert.append(instruction("", "ADD", ["SP", "SP", f"{regs + form.count('i') + 1}"]))
                insert[index].label = ret_addr
                marker = 0
                for y in range(len(program)):
                    if funcLabelName == program[y].label:
                        insert2 = []
                        for z in range(regs):
                            insert2.append(instruction(program[y].label, "PSH", [f"${z+1}"]))
                            program[y].label = ""
                        insert2.append(instruction("", "ADD", ["SP", "SP", str(regs)]))
                        for z in range(form.count("i")):
                            insert2.append(instruction("", "POP", [f"${len(form)-z}"]))
                        insert2.append(instruction("", "SUB", ["SP", "SP", str(regs+form.count("i"))]))
                        program = program[:y] + insert2 + program[y:]
                        marker = y
                        break
                for y in range(marker, len(program)):
                    if program[y].opcode == "RET":
                        insert2 = []
                        for z in range(form.count("o")):
                            insert2.append(instruction(program[y].label, "PSH", [f"${z+1}"]))
                            program[y].label = ""
                        insert2.append(instruction("", "ADD", ["SP", "SP", str(form.count("o"))]))
                        for z in range(regs):
                            insert2.append(instruction("", "POP", [f"${regs-z}"]))
                        insert2.append(instruction("", "ADD", ["SP", "SP", str(form.count("i"))]))
                        insert2.append(instruction("", "POP", [f"${temp+2}"]))
                        insert2.append(instruction("", "SUB", ["SP", "SP", str(len(form) + regs + 1)]))
                        insert2.append(instruction("", "JMP", [f"${temp+2}"]))
                        program = program[:y] + insert2 + program[y+1:]
                program = program[:x] + insert + program[x+1:]
                return False, program
            elif opcode in ["POP", "PSH"]:
                if opcode == "PSH":
                    insert = [
                        instruction(label, "DEC", ["SP","SP"]),
                        instruction("", "STR", ["SP",operandList[0]])
                    ]
                else:
                    insert = [
                        instruction(label, "LOD", [operandList[0],"SP"]),
                        instruction("", "INC", ["SP","SP"])
                    ]
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
                if line.operandList[1][0] != "$" and line.operandList[1] != "SP":
                    program[x].opcode = "IMM"
            if line.opcode == "IMM":
                if line.operandList[1][0] == "$" or line.operandList[1] == "SP":
                    program[x].opcode = "MOV"
            if line.opcode == "RET" and line.operandList != []:
                program[x].opcode = "JMP"
    return program

def countPatternLength(segments):
    segments = " ".join(segments)
    segments = "".join(list(filter(lambda a: a not in " _", segments)))
    return len(segments)

def fixImmediates(program):
    global JMPnching_ops
    for x, line in enumerate(program):
        if line.opcode not in JMPnching_ops and line.opcode != "CAL":
            for y, operand in enumerate(line.operandList):
                if len(operand) > 2:
                    if operand[0] == "0" and operand[1].isalpha():
                        program[x].operandList[y] = str(int(operand, 0))
                if operand[0] == "-":
                    program[x].operandList[y] = str(2**int(ISA.CPU_stats["DATABUS_WIDTH"])-int(operand[1:]))
                if operand[0] == "&":
                    operand = operand[1:]
                    if "+" in operand:
                        operand, c = operand.split("+")
                        c = int(c)
                    elif "-" in operand:
                        operand, c = operand.split("-")
                        c = int(c)
                        c *= -1
                    else:
                        c = 0
                    bits = int(ISA.CPU_stats["DATABUS_WIDTH"])
                    segments = []
                    pattern = operand.split("(")
                    pattern = " _".join(pattern)
                    pattern = pattern.split(")")
                    pattern = " ".join(pattern)
                    pattern = pattern.split()
                    for segment in pattern:
                        segments.append(segment)
                    done = False
                    while not done:
                        for z, part in enumerate(pattern):
                            if done:
                                break
                            if part[0] != "_":
                                continue
                            for w in range(1, len(part)):
                                segments[z] += part[w]
                                if countPatternLength(segments) == bits:
                                    done = True
                                    break
                    segments = " ".join(segments)
                    segments = "".join(list(filter(lambda a: a not in " _", segments)))
                    program[x].operandList[y] = str(int(segments, 2) + c)
                else:
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
    global spisreg
    global fixSP
    global usestacknotreg
    global databuswidth
    spisreg = ISA.CPU_stats['SP_IS_REG']
    usestacknotreg = False
    fixSP = not ISA.CPU_stats['MANUAL_SP_REMOVAL']
    BITS = ISA.CPU_stats['DATABUS_WIDTH']
    databuswidth = int(BITS)
    RUNRAM = ISA.CPU_stats["RUN_RAM"]
    done = False
    while not done:
        for x, line in enumerate(program):
            if line.opcode == "BITS":
                if not eval(f"{ISA.CPU_stats['DATABUS_WIDTH']} {BITS[0]} {BITS[1]}"):
                    print(f"WARNING: this program is designed for a CPU with a databus width {BITS[0]} {BITS[1]}. (Target ISA is {ISA.CPU_stats['DATABUS_WIDTH']})")
                program.pop(x)
            elif line.opcode == "RUN":
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
    flag = False
    for line in program:
        if line.opcode == "STR" or line.opcode == "LOD":
            flag = True
    if flag:
        if RUNRAM:
            for line in program:
                labels.append(line.label)
                operandLists.append(line.operandList)
            for lst in operandLists:
                for item in lst:
                    if item == ".STACK_PTR" and item not in labels:
                        program.append(instruction(item,"DW",[f"{ISA.CPU_stats['SP_LOCATION']}"]))
                        labels.append(item)
                    elif item[:5] == ".RES_" and item not in labels:
                        if int(item[5:]) > maxRes:
                            maxRes = int(item[5:])
                        program.append(instruction(item,"DW",["0"]))
                        labels.append(item)
        else:
            for x, line in enumerate(program):
                for y, operand in enumerate(program[x].operandList):
                    if operand[:5] == ".RES_":
                        if int(operand[5:]) > maxRes:
                            maxRes = int(operand[5:])
                        program[x].operandList[y] = f"#{MINRAM+int(operand[5:])}"
                    if operand == ".STACK_PTR":
                        program[x].operandList[y] = f"{ISA.CPU_stats['SP_LOCATION']}"
                        subflag = False
                        for subline in program:
                            if subline.opcode == "STR" and subline.operandList == [f"{ISA.CPU_stats['SP_LOCATION']}", f"{ISA.CPU_stats['SP_LOCATION']}"]:
                                subflag = True
                                break
                        if not subflag:
                            program.append(instruction("", "STR", [f"{ISA.CPU_stats['SP_LOCATION']}", f"{ISA.CPU_stats['SP_LOCATION']}"]))
    return program

def regSubstitution(program):
  global maxRes
  global usestacknotreg
  global temp
  blocked = ["IMM", "CAL", "DW"]
  for opcode in ISA.Instruction_table:
      if not ISA.Instruction_table.get(opcode, [True])[0]:
          blocked.append(opcode)
  done = False
  if usestacknotreg:
    blocked = blocked + JMPnching_ops
    while not done:
      done = True
      for x, line in enumerate(program):
        if line.opcode in blocked:
          continue
        label = line.label
        offenders = []
        for y, operand in enumerate(line.operandList):
          if operand[0] != "$" and operand != "SP" and operand not in offenders:
            if line.opcode == "LOD" and y == 1:
              ex = True
              continue
            elif line.opcode == "STR" and y == 0:
              ex = True
              continue
            else:
              offenders.append(operand)
        if len(offenders) == 0:
          continue
        program[x].label = ""
        insert = []
        originalMaxRes = maxRes
        buffer = 0
        temp = []
        pushed = []
        for y,offender in enumerate(offenders):
          while (f"${y+1+buffer}" in line.operandList):
            buffer += 1
          insert.append(instruction(label, "PSH", [f"${y+1+buffer}"]))
          pushed.append(f"${y+1+buffer}")
          insert.append(instruction("", "IMM", [f"${y+1+buffer}", offender]))
          temp.append(f"${y+1+buffer}")
          for z, item in enumerate(line.operandList):
            if offender == item:
              program[x].operandList[z] = f"${y+1+buffer}"
          maxRes += 1
          label = ""
        insert.append(program[x])
        temp.reverse()
        for t in temp:
          if t in pushed:
            insert.append(instruction("", "POP", [t]))
        program = program[:x] + insert + program[x+1:]
        done = False
        maxRes = originalMaxRes
        break
  else:
    if temp == 0:
        maxReg = 0
        for line in program:
            if line.opcode == "CAL":
                continue
            for operand in line.operandList:
                if operand[0] == "$":
                    if int(operand[1:]) > maxReg:
                        maxReg = int(operand[1:])
        temp = maxReg
    maxReg = temp
    while not done:
      done = True
      for x, line in enumerate(program):
        if line.opcode in blocked:
          continue
        label = line.label
        used = 1
        offenders = {}
        for y, operand in enumerate(line.operandList):
          if operand[0] != "$" and operand != "SP" and offenders.get(operand, None) == None:
            offenders[operand] = maxReg + used
            used += 1
        if len(offenders) == 0:
          continue
        line.label = ""
        insert = []
        for y,key in enumerate(offenders):
          insert.append(instruction(label, "IMM", [f"${offenders[key]}", f"{key}"]))
          label = ""
        for y, operand in enumerate(line.operandList):
          if operand[0] != "$" and operand != "SP":
            line.operandList[y] = f"${offenders[line.operandList[y]]}"
        insert.append(line)
        program = program[:x] + insert + program[x+1:]
        done = False
        break
  return program

def fixStackPointer(program):
  global maxRes
  global SPreg
  global spisreg
  global fixSP
  done = False
  if spisreg:
    if fixSP:
        if SPreg == 0:
            maxReg = 0
            for line in program:
                if line.opcode == "CAL":
                    continue
                for operand in line.operandList:
                    if operand[0] == "$":
                        if int(operand[1:]) > maxReg:
                            maxReg = int(operand[1:])
            SPreg = maxReg
        for x, line in enumerate(program):
            for y, operand in enumerate(line.operandList):
                if operand == "SP":
                    program[x].operandList[y] = f"${SPreg+1}"
  else:
    while not done:
      done = True
      for x, line in enumerate(program):
        label = line.label
        if "SP" not in line.operandList:
          continue
        regs = []
        for y, operand in enumerate(line.operandList):
          if operand != "SP":
            regs.append(operand)
        chosen = 0
        for y in range(1, 100):
          if f"${y}" not in regs:
            chosen = y
            break
        insert = []
        insert.append(instruction(label, "STR", [f".RES_1", f"${chosen}"]))
        insert.append(instruction("", "LOD", [f"${chosen}", f".STACK_PTR"]))
        for y, operand in enumerate(line.operandList):
          if operand == "SP":
            line.operandList[y] = f"${chosen}"
        line.label = ""
        insert.append(line)
        insert.append(instruction("", "STR", [f".STACK_PTR", f"${chosen}"]))
        insert.append(instruction("", "LOD", [f"${chosen}", f".RES_1"]))
        program = program[:x] + insert + program[x+1:]
        done = False
        break
  return program

def setupStack(program):
  if not ISA.CPU_stats["SP_IS_REG"]:
    insert = [
      instruction("", "IMM", ["$1", str(ISA.CPU_stats["STACK_START"])]),
      instruction("", "STR", [".STACK_PTR", "$1"])
      ]
  else:
    insert = [
      instruction("", "IMM", ["SP", str(ISA.CPU_stats["STACK_START"])])
    ]
  program = insert + program
  return program

def flipStack(program):
    if ISA.CPU_stats["FLIPPED_STACK"]:
        SP_operators = ["INC","ADD","SUB","DEC"]
        for x, ins in enumerate(program):
            if ins.opcode in SP_operators and "SP" in ins.operandList:
                program[x].opcode = SP_operators[(~ SP_operators.index(ins.opcode)) & 3]
    return program

def shiftRAM(program):
    length = ISA.getProgramLength(program)
    for x,line in enumerate(program):
        line = line.split()
        for y,word in enumerate(line):
            if word[0] == "#":
                if word[1:].isnumeric():
                    line[y] = str(int(word[1:]) + length)
                elif word[1:-1].isnumeric():
                    line[y] = str(int(word[1:-1]) + length) + word[-1]
        program[x] = " ".join(line)
    return program

def shiftFunctionRAM(program):
    global MINRAM
    shift = False
    for x, ins in enumerate(program):
        if "#" in ins.label and ")" in ins.label:
            shift = True
        if ins.opcode == "RET":
            shift = False
        if shift:
            for y, operand in enumerate(program[x].operandList):
                if operand[0] == "#" and operand[1:].isnumeric():
                    program[x].operandList[y] = f"#{int(operand[1:]) + MINRAM}"
    return program

def main():
    global operands
    global RUNRAM
    if len(s.argv) > 2: program, done = importProgram(s.argv[2]), False
    else: program, done = importProgram(input("File to compile? (with extension) ")), False
    program = removeComments(program)
    program = convertToInstructions(program)
    try: program = ISA.RawURCL(program)
    except Exception as ex: end(ex,"- no suggestions, problem with ISA designer's raw URCL tweaks. Report this to them if necessary.")
    program = fixImmediates(program)
    program = fixLabels(program)
    program = readHeaders(program)
    if not spisreg: program = fixStackPointer(program)
    for ins in program:
      if ins.opcode in ["PSH","POP","CAL"] or "SP" in ins.operandList:
          program = setupStack(program)
          break
    program = importLibs(program)
    program = reduceLibs(program)
    program = fixLabels(program)
    program = fixImmediates(program)
    program = optimise(program)
    program = regSubstitution(program)
    program = shiftFunctionRAM(program)
    while not done:
        done, program = replaceComplex(program)
        if not spisreg: program = fixStackPointer(program)
        program = fixLabels(program)
        program = fixImmediates(program)
        program = optimise(program)
        program = allocateReservedRAM(program)
        program = regSubstitution(program)
        done, program = replaceComplex(program)
    program = fixStackPointer(program)
    program = flipStack(program)
    try: program, operands = ISA.CleanURCL(program, operands)
    except Exception as ex:end(ex,"- no suggestions, problem with ISA designer's clean URCL tweaks. Report this to them if necessary.")
    max_y = os.get_terminal_size().lines
    maxlen = 0
    for ins in program:
        if len(ins.label) > maxlen:
            maxlen = len(ins.label)
    print(f"\nURCL code:")
    for x, ins in enumerate(program):
        print(f"{ins.label:>{maxlen}} {ins.opcode:<7} {', '.join(ins.operandList)}")
        if x > (max_y//2) - 9:
            print(f"{'':>{maxlen}} ... ({len(program)-1-x} more lines)")
            break
    filename = "URCL_output.urcl"
    if len(s.argv) > 4:
        filename = s.argv[4]
    outfile = open(filename, "w+")
    for ins in program:
        if ins.label != "":
            outfile.write(ins.label + "\n")
        outfile.write(f"{ins.opcode} {', '.join(ins.operandList)}\n")
    outfile.close()
    print(f"URCL code dumped in: {filename}")
    if ISA.__name__ == "ISA_configs.Emulate":
        return
    try:program = convertToISA(program)
    except Exception as ex:end(ex,"- try checking:\n1. Are all the instructions correctly implemented in the ISA's config file? (It is likely that a basic instruction is missing)\n2. Is there a bug in the URCL program, such as JMPnching past the end?",)
    try:program = ISA.LabelISA(program)
    except Exception as ex:end(ex,"- no suggestions, problem with ISA designer's labelled ISA tweaks. Report this to them if necessary.",)
    if not ISA.CPU_stats["MANUAL_LABEL_REMOVAL"]:program = removeISALabels(program)
    else:program = ISA.RemoveLabels(program)
    try:program = ISA.FinalISA(program)
    except Exception as ex:end(ex,"- no suggestions, problem with ISA designer's final ISA tweaks. Report this to them if necessary.",)
    program = shiftRAM(program)
    print(f"\n{ISA.__name__} code:")
    for x, line in enumerate(program):
        print(f"{'':>{maxlen}} {line}")
        if x > (max_y//2) - 9:
            print(f"{'':>{maxlen}} ... ({len(program)-1-x} more lines)")
            break
    filename = f"{ISA.__name__}_output.txt"
    if len(s.argv) > 3:
        filename = s.argv[3]
    outfile = open(filename, "w+")
    for line in program:
        outfile.write(line + "\n")
    outfile.close()
    print(f"{ISA.__name__} code dumped in: {filename}")
    return
if __name__ == "__main__":
    if len(s.argv) > 1:
        exec(f"import ISA_configs.{s.argv[1]} as ISA")
    else:
        try:
            exec(f"import ISA_configs.{input('Compile to which ISA? (without extension) ')} as ISA")
        except Exception as ex:end(ex,"- try checking:\n1. Is it in a different folder to URCL.py?\n2. Are you running URCL.py from elsewhere?",)
    main()