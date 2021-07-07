import sys as s
import os
import copy
class instruction:
  def __init__(self, label, opcode, operandList=[]):
    self.label = label
    self.opcode = opcode
    self.operandList = operandList
class opcode:
  def __init__(self, name, type, complexity):
    self.name = name
    self.type = type
    self.complexity = complexity
class operand:
  def __init__(self, type, value=""):
    self.type = type
    self.value = value
class ISAinstruction:
  def __init__(self, label, instruction):
    self.label = label
    self.instruction = instruction

prefixes = {
  "register": "$",
  "memAddr": "#",
  "label": ".",
  "stackPtr": "SP",
  "bitPattern": "&",
  "tempreg": "^",
  "port": "%"
}
opcodes = {
  "IMPORT": ("header", "core"),
  "BITS": ("header", "core"),
  "MINRAM": ("header", "core"),
  "MINREG": ("header", "core"),
  "MINSTACK": ("header", "core"),
  "RUN": ("header", "core"),

  "ADD": ("arithmetic", "core"),
  "SUB": ("arithmetic", "core"),
  "RSH": ("arithmetic", "core"),
  "LSH": ("arithmetic", "core"),
  "INC": ("arithmetic", "core"),
  "DEC": ("arithmetic", "core"),
  "XOR": ("arithmetic", "core"),
  "AND": ("arithmetic", "core"),
  "OR":  ("arithmetic", "core"),
  "NOR": ("arithmetic", "core"),
  "NAND":("arithmetic", "core"),
  "XNOR":("arithmetic", "core"),
  "NOT": ("arithmetic", "core"),
  "MOV": ("register", "core"),
  "IMM": ("register", "core"),
  "LOD": ("register", "core"),
  "STR": ("register", "core"),
  "JMP": ("branch", "core"),
  "BRZ": ("branch", "core"),
  "BNZ": ("branch", "core"),
  "BRN": ("branch", "core"),
  "BRP": ("branch", "core"),
  "NOP": ("other", "core"),
  "HLT": ("other", "core"),

  "MLT": ("arithmetic", "complex"),
  "DIV": ("arithmetic", "complex"),
  "MOD": ("arithmetic", "complex"),
  "CAL": ("branch", "complex"),
  "RET": ("branch", "complex"),
  "PSH": ("register", "complex"),
  "POP": ("register", "complex"),
  "BRL": ("branch", "complex"),
  "BRG": ("branch", "complex"),
  "BRE": ("branch", "complex"),
  "BNE": ("branch", "complex"),
  "BOD": ("branch", "complex"),
  "BEV": ("branch", "complex"),
  "BLE": ("branch", "complex"),
  "BGE": ("branch", "complex"),
  "BZR": ("branch", "complex"),
  "BZN": ("branch", "complex"),
  "IN": ("other", "complex"),
  "OUT": ("other", "complex"),
  "BSR": ("arithmetic", "complex"),
  "BSL": ("arithmetic", "complex"),
  "SRS": ("arithmetic", "complex"),
  "BSS": ("arithmetic", "complex"),
  "CMP": ("arithmetic", "complex"),
  "ADC": ("arithmetic", "complex"),
  "SBB": ("arithmetic", "complex"),
  "NEG": ("arithmetic", "complex"),
  "SETE": ("arithmetic", "complex"),
  "SETNE": ("arithmetic", "complex"),
  "SETG": ("arithmetic", "complex"),
  "SETL": ("arithmetic", "complex"),
  "SETGE": ("arithmetic", "complex"),
  "SETLE": ("arithmetic", "complex"),
  "LLOD": ("other", "complex"),
  "LSTR": ("other", "complex"),
}
cmplx_subs = {
  # BASIC TRANSLATIONS
  "SUB": [
    "NEG ^1, <C>",
    "ADD <A>, <B>, ^1"
    ],
  "JMP": [
    "BGE <A>, $0, $0"
    ],
  "MOV": [
    "ADD <A>, <B>, $0"
    ],
  "NOP": [
    "MOV $0, $0"
    ],
  "IMM": [
    "ADD <A>, <B>, $0"
    ],
  "LSH": [
    "ADD <A>, <B>, <B>"
    ],
  "INC": [
    "ADD <A>, <B>, 1"
    ],
  "DEC": [
    "ADD <A>, <B>, &(1)"
    ],
  "NEG": [
    "NOT <A>, <B>",
    "INC <A>, <A>"
    ],
  "AND": [
    "NOT ^1, <B>",
    "NOT ^2, <C>",
    "NOR <A>, ^1, ^2"
    ],
  "OR": [
    "NOR <A>, <B>, <C>",
    "NOT <A>, <A>"
    ],
  "NOT": [
    "NOR <A>, <B>, $0"
    ],
  "XNOR": [
    "XOR <A>, <B>, <C>"
    "NOT <A>, <A>"
  ],
  "XOR": [
    "AND <A>, <B>, <C>",
    "NOR ^1, <B>, <C>",
    "NOR <A>, <A>, ^1",
  ],
  "NAND": [
    "NOT ^1, <B>",
    "NOT <A>, <C>",
    "NOR <A>, <A>, ^1",
    "NOT <A>, <A>"
  ],
  "BRL": [
    "BGE +2, <B>, <C>",
    "JMP <A>",
    "NOP"
  ],
  "BRG": [
    "BGE +2, <C>, <B>",
    "JMP <A>",
    "NOP"
  ],
  "BRE": [
    "BGE +2, <B>, <C>",
    "JMP +4",
    "BGE +2, <C>, <B>",
    "JMP +2",
    "JMP <A>",
    "NOP"
  ],
  "BNE": [
    "BGE +2, <B>, <C>",
    "JMP +2",
    "BGE +2, <C>, <B>",
    "JMP <A>",
    "NOP"
  ],
  "BOD": [
    "AND ^1, <B>, 1",
    "BGE <A>, ^1, 1"
  ],
  "BEV": [
    "AND ^1, <B>, 1",
    "BGE +2, ^1, 1",
    "JMP <A>",
    "NOP"
  ],
  "BLE": [
    "BGE <A>, <C>, <B>"
  ],
  "BRZ": [
    "BGE +2, <B>, 1",
    "JMP <A>",
    "NOP"
  ],
  "BNZ": [
    "BGE <A>, <B>, 1"
  ],
  "BRN": [
    "BGE <A>, <B>, &1(0)"
  ],
  "BRP": [
    "BGE +2, <B>, &1(0)",
    "JMP <A>",
    "NOP"
  ],
  "PSH": [
    "DEC SP, SP",
    "STR SP, <A>"
  ],    
  "POP": [
    "LOD <A>, SP",
    "INC SP, SP"
  ],
  "CAL": [
    "PSH +2",
    "JMP <A>",
    "NOP"
  ],
  "RET": [
    "POP ^1",
    "JMP ^1"
  ],
  "HLT": [
    "JMP +0"
  ],
  "CPY": [
    "LOD ^1, <B>",
    "STR <A>, ^1"
  ],
  # COMPLEX TRANSLATIONS
  "MLT": [ # IMPROVED
    "IMM <A>, 0",
    "BRZ +5, <C>",
    "MOV ^1, <C>",
    "MOV ^2, <B>",
    "DEC ^1, ^1",
    "ADD <A>, <A>, ^2",
    "BNZ -2, ^1",
    "NOP"
  ],
  "DIV": [ # IMPROVED
    "IMM <A>, 0",
    "BRL +5, <B>, <C>",
    "MOV ^1, <B>",
    "MOV ^2, <C>"
    "INC <A>, <A>",
    "SUB ^1, ^1, ^2",
    "BGE -2, ^1, ^2",
    "NOP"
  ],
  "MOD": [
    "MOV ^1, <C>",
    "MOV <A>, <B>",
    "BRL +3, <B>, ^1",
    "SUB <A>, <A>, ^1",
    "JMP -2"
  ],
  "BSR": [
    "MOV ^1, <C>",
    "MOV <A>, <B>",
    "BRZ +4, ^1",
    "RSH <A>, <A>",
    "DEC ^1, ^1",
    "JMP -3",
    "NOP"
  ],
  "BSL": [
    "MOV ^1, <C>",
    "MOV <A>, <B>",
    "BRZ +4, ^1",
    "LSH <A>, <A>",
    "DEC ^1, ^1",
    "JMP -3",
    "NOP"
  ],
  "SRS": [
    "BRN +3, <B>",
    "RSH <A>, <B>",
    "JMP +3",
    "RSH <A>, <B>",
    "ADD <A>, <A>, &1(0)"
  ],
  "BSS": [
    "MOV ^1, <C>",
    "MOV <A>, <B>",
    "BRZ +4, ^1",
    "SRS <A>, <A>",
    "DEC ^1, ^1",
    "JMP -3",
    "NOP"
  ],
  "SETE": [ # IMPROVED
    "IMM <A>, 0",
    "BNE +2, <B>, <C>",
    "IMM <A>, &(1)",
    "NOP"
  ],
  "SETNE": [ # IMPROVED
    "IMM <A>, 0",
    "BRE +2, <B>, <C>",
    "IMM <A>, &(1)",
    "NOP"
  ],
  "SETG": [ # IMPROVED
    "IMM <A>, 0",
    "BLE +2, <B>, <C>",
    "IMM <A>, &(1)",
    "NOP"
  ],
  "SETL": [ # IMPROVED
    "IMM <A>, 0",
    "BGE +2, <B>, <C>",
    "IMM <A>, &(1)",
    "NOP"
  ],
  "SETGE": [ # IMPROVED
    "IMM <A>, 0",
    "BRL +2, <B>, <C>",
    "IMM <A>, &(1)",
    "NOP"
  ],
  "SETLE": [ # IMPROVED
    "IMM <A>, 0",
    "BRG +2, <B>, <C>",
    "IMM <A>, &(1)",
    "NOP"
  ],
  "LLOD": [
    "ADD <A>, <B>, <C>",
    "LOD <A>, <A>"
  ],
  "LSTR": [
    "ADD ^1, <A>, <B>",
    "STR <C>, ^1"
  ],
}
end = (lambda ex, tag: input(f"\n--- Something went wrong :( ---\n\n{ex} {tag}\n") and s.exit())

def importProgram(name):
    try:
        return [line.strip() for line in open(name, "r", encoding="utf8")]
    except Exception as ex:
        end(ex, "- try checking:\n1. Is it in a different folder to URCL.py?\n2. Are you running URCL.py from elsewhere?\n 3. 'invalid syntax'? An error with the ISA designer's code.",)

def parseURCL(program):
  program = removeComments(program)
  program = convertToInstructions(program)
  program = convertOperands(program)
  program = fixOperands(program)
  return program

def removeComments(program):
    # Removes all comments from the code
    # Changes all registers denoted with R to $
    # Changes all memory addresses denoted with M to #
    # Removes any empty lines
    code = []
    for x, line in enumerate(program):
      line = line.split("//")[0]
      line = line.split(";")[0]
      line = line.split()
      for y, token in enumerate(line):
        if token[0] == "R" and token[1:].rstrip(",").isnumeric():
          line[y] = "$" + token[1:]
        elif token[0] == "M" and token[1:].rstrip(",").isnumeric():
          line[y] = "#" + token[1:]
      line = " ".join(line)
      if line != "":
        code.append(line)
    return list(filter(None, code))

def convertToInstructions(program):
    # Converts a whole program to instruction objects
    # Removes any empty lines
    code = []
    labels = []
    for x, ins in enumerate(program):
      insNew = instruction([], "", [])
      ins = ins.split()
      if ins[0][0] == ".":
        labels.append(ins[0][1:])
        continue
      else:
        insNew.opcode = ins[0]
        insNew.label = labels
        insNew.operandList = [y.rstrip(",") for y in ins[1:]]
      code.append(insNew)
      labels = []
    return list(filter(None, code))

def convertOperands(program):
  # Converts all operands to operand objects
  for x, ins in enumerate(program):
    program[x].opcode = opcode(ins.opcode, *opcodes[ins.opcode])
    for y, lab in enumerate(program[x].label):
      program[x].label[y] = operand("label", lab)
    for y, opr in enumerate(program[x].operandList):
      if opr[0] == "$":
        program[x].operandList[y] = operand("register", int(opr[1:]))
      elif opr[0] == "#":
        program[x].operandList[y] = operand("memAddr", int(opr[1:]))
      elif opr[0] == ".":
        program[x].operandList[y] = operand("label", opr[1:])
      elif opr[0] == "+" or opr[0] == "-" and ins.opcode.type == "branch":
        program[x].operandList[y] = operand("relativeAddr", int(opr))
      elif opr == "SP":
        program[x].operandList[y] = operand("stackPtr")
      elif opr[0] == "&":
        program[x].operandList[y] = operand("bitPattern", opr[1:])
      elif opr[0] == "%":
        program[x].operandList[y] = operand("port", opr[1:])
      elif opr[0] == "<" and program[x].opcode.type != "header":
        program[x].operandList[y] = operand("placeholder", opr[1])
      elif opr[0] == "^":
        program[x].operandList[y] = operand("tempreg", int(opr[1:]))
      else:
        try:
          program[x].operandList[y] = operand("number", int(opr, base=0))
        except:
          program[x].operandList[y] = operand("other", opr)
  return program

def readHeaders(program):
  # Reads and removes the program headers
  global MINRAM
  global MINREG
  global MINSTACK
  global MAXREG
  global IMPORTS
  done = False
  while not done:
    done = True
    for x, ins in enumerate(program):
      for y, opr in enumerate(ins.operandList):
        if opr.type == "register":
          if opr.value > MAXREG:
            MAXREG = opr.value
      if ins.opcode.type == "header":
        done = False
        if ins.opcode.name == "MINRAM":
          MINRAM = ins.operandList[0].value
        elif ins.opcode.name == "MINSTACK":
          MINSTACK = ins.operandList[0].value
        elif ins.opcode.name == "MINREG":
          MINREG = ins.operandList[0].value
        elif ins.opcode.name == "IMPORT":
          for opr in ins.operandList:
            IMPORTS.append(opr.value)
        program.pop(x)
        break
  return program

def evaluateBitPattern(bitPattern):
  global BITS
  # Converts operand objects of type "bitPattern" to operand objects of type "number"
  # Allows bit patterns in the form &(1)(0)+c where c is a constant
  opr = bitPattern.value
  c = 0
  if "+" in opr:
    opr, c = opr.split("+")
    c = int(c)
  elif "-" in opr:
    opr, c = opr.split("-")
    c = -int(c)
  segments = []
  pattern = opr.split("(")
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
              segmentString = "".join(segments)
              if segmentString.count("0") + segmentString.count("1") == BITS:
                  done = True
                  break
  segments = " ".join(segments)
  segments = "".join(list(filter(lambda a: a not in " _", segments)))
  return operand("number", int(segments, 2) + c)

def fixOperands(program):
  # Converts relative addresses to labels
  # Negative immediates become signed positive immediates
  # Bit patterns become immediates
  global labelCount
  global BITS
  global MAXTEMPREG
  for x, ins in enumerate(program):
    for y, opr in enumerate(program[x].operandList):
      if opr.type == "relativeAddr":
        program[x + opr.value].label.append(operand("label", f"__label__{labelCount}"))
        program[x].operandList[y] = operand("label", f"__label__{labelCount}")
        labelCount += 1
      elif opr.type == "number" and opr.value < 0:
        program[x].operandList[y].value = 2**BITS + opr.value
      elif opr.type == "bitPattern":
        value = evaluateBitPattern(opr)
        program[x].operandList[y] = value
  return program

def parseIns(ins):
  # Fully parses an isolated URCL instruction, including operands
  insNew = instruction([], "", [])
  ins = ins.split()
  insNew.opcode = ins[0]
  insNew.operandList = [y.rstrip(",") for y in ins[1:]]
  ins = insNew
  ins.opcode = opcode(ins.opcode, *opcodes[ins.opcode])
  for y, lab in enumerate(ins.label):
    ins.label[y] = operand("label", lab[1:])
  for y, opr in enumerate(ins.operandList):
    if opr[0] == "$":
      ins.operandList[y] = operand("register", int(opr[1:]))
    elif opr[0] == "#":
      ins.operandList[y] = operand("memAddr", int(opr[1:]))
    elif opr[0] == ".":
      ins.operandList[y] = operand("label", opr[1:])
    elif opr[0] == "+" or opr[0] == "-" and ins.opcode.type == "branch":
      ins.operandList[y] = operand("relativeAddr", int(opr))
    elif opr == "SP":
      ins.operandList[y] = operand("stackPtr")
    elif opr[0] == "&":
      ins.operandList[y] = operand("bitPattern", opr[1:])
    elif opr[0] == "<" and ins.opcode.type != "header":
      ins.operandList[y] = operand("placeholder", opr[1])
    elif opr[0] == "^":
      ins.operandList[y] = operand("tempreg", int(opr[1:]))
    else:
      try:
        ins.operandList[y] = operand("number", int(opr))
      except:
        if len(opr) == 1:
          ins.operandList[y] = operand("number", ord(opr))
        else:
          ins.operandList[y] = operand("other", opr)
  return ins

def replaceComplex(program):
  # Replaces unsupported instructions with lower-level translations where possible
  # Uses tempregs where necessary
  # TODO: Stop using tempregs when they are no longer available, use virtual registers instead
  global labelCount
  global MAXTEMPREG
  global DEPTH
  done = False
  alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  while not done:
    done = True
    for x, ins in enumerate(program):
      if ISA.Instruction_table.get(ins.opcode.name) == None and ISA.Instruction_table.get(getOperandStructure(ins)) == None:
        if cmplx_subs.get(getOperandStructure(ins)) == None or ins.opcode.name == "NOP":
          if cmplx_subs.get(ins.opcode.name) == None or ins.opcode.name == "NOP":
            continue
          else:
            translation = copy.deepcopy(cmplx_subs.get(ins.opcode.name))
        else:
          translation = copy.deepcopy(cmplx_subs.get(getOperandStructure(ins)))
        lab = copy.deepcopy(ins.label)
        done = False
        tempmaxtempreg = 0
        for opr in ins.operandList:
          if opr.type == "tempreg" and opr.value > tempmaxtempreg:
            tempmaxtempreg = opr.value
        MAXTEMPREG += tempmaxtempreg
        if translation != None:
          translation = parseURCL(translation)
          tempmaxtempreg2 = 0
          for z, tins in enumerate(translation):
            for w, topr in enumerate(tins.operandList):
              if topr.type == "tempreg":
                if topr.value > tempmaxtempreg2:
                  tempmaxtempreg2 = topr.value
          original2 = MAXTEMPREG
          MAXTEMPREG = tempmaxtempreg2
          translation = regSubstitution(translation)
          MAXTEMPREG = original2
          for z, tins in enumerate(translation):
            for w, tlab in enumerate(tins.label):
              if tlab.value != "":
                translation[z].label[w].value = tlab.value + f"__{labelCount}"
            for w, topr in enumerate(tins.operandList):
              if topr.type == "tempreg":
                translation[z].operandList[w].value += MAXTEMPREG
              elif topr.type == "label":
                translation[z].operandList[w].value = topr.value + f"__{labelCount}"
          tempmaxtempreg3 = 0
          for z, tins in enumerate(translation):
            for w, topr in enumerate(tins.operandList):
              if topr.type == "tempreg":
                if topr.value > tempmaxtempreg3:
                  tempmaxtempreg3 = topr.value
          original3 = MAXTEMPREG
          MAXTEMPREG = tempmaxtempreg + tempmaxtempreg3
          DEPTH += 1
          translation = replaceComplex(copy.deepcopy(translation))
          MAXTEMPREG = original3
          for y, opr in enumerate(ins.operandList):
            for z, tins in enumerate(translation):
              for w, topr in enumerate(tins.operandList):
                if topr.type == "placeholder" and topr.value == alphabet[y]:
                  translation[z].operandList[w] = opr
        else:
          input(f"Cannot translate:\n  - No URCL or ISA translations are available for {ins.opcode.name}.\nFull instruction:\n  - {ins.opcode.name} {', '.join([str(x.value) for x in ins.operandList])}")
          s.exit()
        MAXTEMPREG -= tempmaxtempreg
        program = program[:x] + translation + program[x+1:]
        program[x].label += lab
        labelCount += 1
      else:
        continue
      break
  return program

def printIns(ins):
  # Prints a single URCL instruction, with labels
  for lab in ins.label:
    print("." + lab.value)
  print(ins.opcode.name + " " + ", ".join([prefixes.get(opr.type, "") + str(opr.value) for opr in ins.operandList]))
  return

def regSubstitution(program):
  # Replaces unsupported operand structures with register-only versions
  # Example: ADD $1, $2, 15   ->   IMM $3, 15; ADD $1, $2, $3
  global MAXREG
  global MAXTEMPREG
  done = False
  exempt = ("IMM", "header", "pragma", "IN")
  while not done:
    done = True
    for x, ins in enumerate(program):
      newOpcode = getOperandStructure(ins)
      if ISA.Instruction_table.get(newOpcode) == None and ins.opcode.name not in exempt and ins.opcode.type not in exempt:
        swap = []
        hit = False
        insert = []
        lab = []
        for y, opr in enumerate(program[x].operandList):
          if opr.type not in ("register", "stackPtr", "tempreg", "placeholder") and ins.operandList != [] and not (y == 0 and ins.opcode.name == "OUT"):
            if not hit:
              lab = program[x].label
              program[x].label = []
              hit = True
              done = False
            if (opr.type, opr.value) not in swap:
              swap.append((opr.type, opr.value))
            for s, val in enumerate(swap):
              if val == (opr.type, opr.value):
                insert.append(instruction([], opcode("IMM", "register", "core"), [operand("tempreg", s+1+MAXTEMPREG), opr]))
                program[x].operandList[y] = operand("tempreg", s+1+MAXTEMPREG)
        if hit:
          program = program[:x] + insert + program[x:]
          program[x].label = lab
          break
  return program

def replaceTempReg(program):
  # Turns tempregs into real registers
  global MAXREG
  for x, ins in enumerate(program):
    for y, opr in enumerate(program[x].operandList):
      if opr.type == "tempreg":
        program[x].operandList[y].type = "register"
        program[x].operandList[y].value += MAXREG
  return program

def storeRegInMem(program):
  # UNUSED - replaced high registers with virtual ones
  # Example: CPU supports $1-6, so $7+ would be stored in RAM
  global MAXREG
  global ISAREGS
  special = ["STR", "OUT"]
  useStack = False
  totalregs = 0
  regList = []
  for ins in program:
    for opr in ins.operandList:
      if opr.type == "SP":
        if ISA.CPU_stats["SP_IS_GPR"] and not useStack:
          totalregs += 1
        useStack = True
      if opr.type == "register" and opr.value not in regList:
        regList.append(opr.value)
        totalregs += 1
  if totalregs <= ISAREGS:
    return program
  else:
    done = False
    for x, ins in enumerate(program):
      for y, opr in enumerate(program[x].operandList):
        if program[x].operandList[y].type == "memAddr":
          program[x].operandList[y].value += totalregs - ISAREGS + 1
    while not done:
      done = True
      for x, ins in enumerate(program):
        mappings = {}
        regsUsed = []
        insert1 = []
        lab = ins.label
        for y, opr in enumerate(program[x].operandList):
          if opr.type == "register":
            regsUsed.append(opr.value)
        for y, opr in enumerate(program[x].operandList):
          if (opr.type == "register") and ((opr.value > ISAREGS) or (opr.value == ISAREGS and ISA.CPU_stats["SP_IS_GPR"])):
            if done:
              done = False
              program[x].label = []
            for z in range(1, 10):
              if z not in regsUsed:
                if mappings.get(opr.value) == None:
                  mappings[opr.value] = (z, y)
                else:
                  mappings[opr.value] = (*mappings[opr.value], y)
                program[x].operandList[y].value = z
                break
        if done:
          continue
        keys = []
        for key in mappings:
          keys.append(key)
          insert1.append(parseIns(f"PSH ${mappings[key][0]}"))
          if (mappings[key][1] != 0 or ins.opcode.name in special) and not ISA.Instruction_table.get("LOD", [True])[0]:
            insert1 += [
              parseIns(f"LOD ${mappings[key][0]}, #{key-ISAREGS}"),
            ]
          elif (mappings[key][1] != 0 or ins.opcode.name in special):
            insert1 += [
              parseIns(f"IMM ${mappings[key][0]}, #{key-ISAREGS}"),
              parseIns(f"LOD ${mappings[key][0]}, ${mappings[key][0]}"),
            ]
        insert1.append(program[x])
        keys.reverse()
        for key in keys:
          if (mappings[key][1] != 0 or ins.opcode.name in special):
            insert1.append(parseIns(f"POP ${mappings[key][0]}"))
          else:
            if not ISA.Instruction_table.get("STR", [True])[0]:
              insert1 += [
                parseIns(f"STR #{key-ISAREGS} ${mappings[key][0]}"),
                parseIns(f"POP ${mappings[key][0]}")
              ]
            else:
              key2 = 1
              if mappings[key][0] == 1:
                key2 = 2
              insert1 += [
                parseIns(f"PSH ${key2}"),
                parseIns(f"IMM ${key2}, #{key-ISAREGS}"),
                parseIns(f"STR ${key2}, ${mappings[key][0]}"),
                parseIns(f"POP ${key2}"),
                parseIns(f"POP ${mappings[key][0]}")
              ]
            pass
        program = program[:x] + insert1 + program[x+1:]
        program[x].label = lab
        break
  return program

def getOperandStructure(ins):
  # Gets the operand structure of the instruction
  tag = ""
  for o, opr in enumerate(ins.operandList):
    if opr.type == "register" or opr.type == "stackPtr":
        tag += "r"
    else:
        tag += "i"
  if tag == "r"*len(tag) or "_" in ins.opcode.name:
    return ins.opcode.name
  else:
    return ins.opcode.name + "_" + tag

def optimise(program):
  # Performs basic optimisations:
  # - removes NOP
  done = False
  while not done:
    done = True
    for x, ins in enumerate(program):
      if ins.opcode.name == "NOP":
        program[x+1].label += program[x].label
        program = program[:x] + program[x+1:]
        done = False
        break
  return program

def convertToISA(program):
  # Replaces URCL instructions with provided ISA translations
  ISAprogram = []
  alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  for ins in program:
    newOpcode = getOperandStructure(ins)
    translation = copy.deepcopy(ISA.Instruction_table.get(newOpcode, []))
    if translation == []:
      translation = copy.deepcopy(ISA.Instruction_table.get(ins.opcode.name, []))
      if translation == []:
        input(f"Cannot translate:\n  - No URCL or ISA translations are available for {ins.opcode.name}.\nFull instruction:\n  - {ins.opcode.name} {', '.join([str(x.value) for x in ins.operandList])}")
        s.exit()
    for t, tins in enumerate(translation):
      translation[t] = ISAinstruction([], translation[t])
      if t == 0:
        translation[t].label = [f".{lbl.value}%" for lbl in ins.label]
      for o, opr in enumerate(ins.operandList):
        if opr.type != "label":
          translation[t].instruction = translation[t].instruction.replace(f"<{alphabet[o]}>", prefixes.get(opr.type, "") + str(opr.value))
        else:
          translation[t].instruction = translation[t].instruction.replace(f"<{alphabet[o]}>", prefixes.get(opr.type, "") + str(opr.value) + "%")
    ISAprogram += translation
  return ISAprogram

def printURCL(program):
  # Prints a full URCL program
  for ins in program:
    printIns(ins)
  return

def checkStackUsage(program):
  # Checks whether or not the program uses the stack
  global STACKUSAGE
  for ins in program:
    if STACKUSAGE:
      break
    if ins.opcode.name in ("PSH", "POP"):
      STACKUSAGE = True
      break
    for opr in ins.operandList:
      if opr.type == "stackPtr":
        STACKUSAGE = True
        break
  return

def fixStack(program):
  # Flips the stack if necessary, and prunes "SP" if necessary
  global MAXREG
  for x, ins in enumerate(program):
    for y, opr in enumerate(ins.operandList):
      if opr.type == "register":
        if opr.value > MAXREG:
          MAXREG = opr.value
  swapped = {
    "INC":"DEC",
    "DEC":"INC",
    "ADD":"SUB",
    "SUB":"ADD"
  }
  newSP = int(ISA.CPU_stats["SP_LOCATION"])
  if newSP == 0:
    newSP = MAXREG + 1
  program = [instruction([], opcode("IMM", "register", "core"), [operand("stackPtr"), operand("number", int(ISA.CPU_stats["SP_VALUE"]))])] + copy.deepcopy(program)
  for x, ins in enumerate(program):
    if ins.opcode.name in ("DEC","INC","ADD","SUB") and ISA.CPU_stats["REVERSED_STACK"]:
      program[x].opcode.name = swapped[ins.opcode.name]
    if not ISA.CPU_stats["KEEP_SP"]:
      for y, opr in enumerate(program[x].operandList):
        if opr.type == "stackPtr":
          program[x].operandList[y] = operand("register", newSP)
  return program

def initialiseGlobals():
  # Initialise global variables for the program to use
  global labelCount
  labelCount = 0
  global BITS
  BITS = int(ISA.CPU_stats["DATABUS_WIDTH"])
  global MINRAM
  MINRAM = 0
  global MINSTACK
  MINSTACK = 0
  global MINREG
  MINREG = 0
  global RUNRAM
  RUNRAM = ISA.CPU_stats["RUN_RAM"]
  global MAXREG
  MAXREG = 0
  global ISAREGS
  ISAREGS = int(ISA.CPU_stats["REGISTERS"])
  global MAXTEMPREG
  MAXTEMPREG = 0
  global STACKUSAGE
  STACKUSAGE = False
  global IMPORTS
  IMPORTS = []
  global DEPTH
  DEPTH = 0
  return

def removeISALabels(program):
  # Removes labels from ISA code
  labels = {}
  for x, ins in enumerate(program):
    for lbl in ins.label:
      labels[lbl] = x
    program[x].label = []
  for x, ins in enumerate(program):
    for lbl in labels:
      program[x].instruction = program[x].instruction.replace(lbl, str(labels[lbl]))
  return program

def shiftRAM(program):
  # Shifts memory addresses in ISA code
  for x, ins in enumerate(program):
    ins = ins.instruction.split()
    for o, opr in enumerate(ins):
      if opr[0] == "#" and opr[1:].rstrip(",;"):
        ins[o] = f"#{int(opr[1:].rstrip(',;'))+len(program)}"
        program[x].instruction = " ".join(ins)
  return program

def fixPorts(program):
  # Replaces %PORTs with constants
  for x, ins in enumerate(program):
    for y, opr in enumerate(program[x].operandList):
      if opr.type == "port":
        program[x].operandList[y] = operand("number", ISA.Port_table.get("%" + opr.value))
  return program

def main():
  global opcodes
  global STACKUSAGE
  global MAXREG
  if len(s.argv) > 2:
    program = importProgram(s.argv[2])
  else:
    program = importProgram(input("File to compile? (with extension) "))
  program = parseURCL(program)
  try: program, opcodes = ISA.RawURCL(program, opcodes)
  except Exception as ex: end(ex,"- no suggestions, problem with ISA designer's raw URCL tweaks. Report this to them if necessary.")
  program = regSubstitution(program)
  program = readHeaders(program)
  program = replaceComplex(program)
  checkStackUsage(program)
  MAXREG = 0
  for x, ins in enumerate(program):
    for y, opr in enumerate(ins.operandList):
      if opr.type == "register":
        if opr.value > MAXREG:
          MAXREG = opr.value
  program = replaceTempReg(program)
  if STACKUSAGE:
    program = fixStack(program)
  program = optimise(program)
  try: program, opcodes = ISA.CleanURCL(program, opcodes)
  except Exception as ex: end(ex,"- no suggestions, problem with ISA designer's clean  URCL tweaks. Report this to them if necessary.")
  max_y = os.get_terminal_size().lines
  print(f"\nURCL code:")
  for x, ins in enumerate(program):
    printIns(ins)
    if x > (max_y//2) - 9:
      print(f"... ({len(program)-1-x} more lines)")
      break
  filename = "URCL_output.urcl"
  if len(s.argv) > 4:
      filename = s.argv[4]
  outfile = open(filename, "w+")
  for ins in program:
      for lbl in ins.label:
          outfile.write("." + lbl.value + "\n")
      outfile.write(ins.opcode.name + " " + ", ".join([prefixes.get(opr.type, "") + str(opr.value) for opr in ins.operandList]) + "\n")
  outfile.close()
  print(f"URCL code dumped in: {filename}")
  if ISA.__name__ in ("ISA_configs.Emulate","ISA_configs.Core"):
      return
  program = fixPorts(program)
  program = convertToISA(program)
  try:program = ISA.LabelISA(program)
  except Exception as ex:end(ex,"- no suggestions, problem with ISA designer's labelled ISA tweaks. Report this to them if necessary.")
  if ISA.CPU_stats["REMOVE_LABELS"]:
    program = removeISALabels(program)
  if ISA.CPU_stats["SHIFT_RAM"] and ISA.CPU_stats["RUN_RAM"]:
    program = shiftRAM(program)
  try:program = ISA.FinalISA(program)
  except Exception as ex:end(ex,"- no suggestions, problem with ISA designer's final ISA tweaks. Report this to them if necessary.")
  print(f"\n{ISA.__name__} code:")
  for x, line in enumerate(program):
    if line.label != []:
      print(f"{[lab + ' ' for lab in line.label]}")
    print(line.instruction)
    if x > (max_y//2) - 9:
        print(f"... ({len(program)-1-x} more lines)")
        break
  filename = f"{ISA.__name__}_output.txt"
  if len(s.argv) > 3:
      filename = s.argv[3]
  outfile = open(filename, "w+")
  for line in program:
    if line.label != []:
      for lab in line.label:
        outfile.write(lab + "\n")
    outfile.write(line.instruction + "\n")
  outfile.close()
  print(f"{ISA.__name__} code dumped in: {filename}")
  return
if __name__ == "__main__":
  if len(s.argv) > 1:
    exec(f"import ISA_configs.{s.argv[1]} as ISA")
  else:
    try:
      exec(f"import ISA_configs.{input('Compile to which ISA? (without extension) ')} as ISA")
    except Exception as ex:
      end(ex,"- try checking:\n1. Is it in a different folder to URCL.py?\n2. Are you running URCL.py from elsewhere?",)
  initialiseGlobals()
  main()
# USAGE: (optional, file can be double-clicked)
# py URCL.py {ISA} {program.urcl} {ISA_outfile.txt} {URCL_outfile.txt}