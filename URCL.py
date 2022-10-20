from lib2to3.pytree import convert
import sys as s
import os
import copy
import math
import time

validPragmas = {
    "DuplicateDefines": [
        ["error", "warning", "silent"],
        ["ignore", "overwrite"]]
}

defaultPragmas = {
    "DuplicateDefines": ["warning", "overwrite"]
}

pragmas = defaultPragmas

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
  def __init__(self, type, value="", word=0):
    self.type = type
    self.value = value
    self.word = word
  def equals(self, opr2):
    if self.type == opr2.type and self.value == opr2.value and self.word == opr2.word:
      return True
    else:
      return False
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
  "MINHEAP": ("header", "core"),
  "MINREG": ("header", "core"),
  "MINSTACK": ("header", "core"),
  "RUN": ("header", "core"),
  
  "@NEXT": ("pragma", "other"),
  "@MWADDR": ("pragma", "other"),
  "@MWLABEL": ("pragma", "other"),
  "@MWSP": ("pragma", "other"),
  "@MWFULL": ("pragma", "other"),
  "@PTR": ("pragma", "other"),
  "@UNPTR": ("pragma", "other"),

  "@^": ("pragma", "other"),
  "@V": ("pragma", "other"),

  "MULTI_MOV": ("multiword", "other"),
  "MULTI_ADD": ("multiword", "other"),
  "MULTI_SUB": ("multiword", "other"),
  "MULTI_MULTI_ADD": ("multiword", "other"),
  "MULTI_MULTI_SUB": ("multiword", "other"),
  "MULTI_LOD": ("multiword", "other"),
  "MULTI_STR": ("multiword", "other"),

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
  "BRC": ("branch", "core"),
  "BNC": ("branch", "core"),
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
  "SETC": ("arithmetic", "complex"),
  "SETNC": ("arithmetic", "complex"),
  "LLOD": ("other", "complex"),
  "LSTR": ("other", "complex"),
}
cmplx_subs = {
  # BASIC TRANSLATIONS
  "SUB": [
    "@^",
    "NEG ^1, <C>",
    "ADD <A>, <B>, ^1",
    "@V"
    ],
  "JMP": [
    "BGE <A>, $0, $0"
    ],
  "MOV": [
    "ADD <A>, <B>, $0"
    ],
  "LSH": [
    "ADD <A>, <B>, <B>"
    ],
  "INC": [
    "ADD <A>, <B>, 1"
    ],
  "DEC": [
    "ADD <A>, <B>, -1"
    ],
  "NEG": [
    "NOT <A>, <B>",
    "INC <A>, <A>"
    ],
  "AND": [
    "@^",
    "NOT ^1, <B>",
    "@^",
    "NOT ^2, <C>",
    "NOR <A>, ^1, ^2",
    "@V",
    "@V"
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
    "@^",
    "NOR ^1, <B>, <C>",
    "NOR <A>, <A>, ^1",
    "@V"
  ],
  "NAND": [
    "@^",
    "NOT ^1, <B>",
    "NOT <A>, <C>",
    "NOR <A>, <A>, ^1",
    "@V",
    "NOT <A>, <A>"
  ],
  "BRL": [
    "BGE ~2, <B>, <C>",
    "JMP <A>",
    "NOP"
  ],
  "BRG": [
    "BGE ~2, <C>, <B>",
    "JMP <A>",
    "NOP"
  ],
  "BRE": [
    "BGE ~2, <B>, <C>",
    "JMP ~4",
    "BGE ~2, <C>, <B>",
    "JMP ~2",
    "JMP <A>",
    "NOP"
  ],
  "BNE": [
    "BGE ~2, <B>, <C>",
    "JMP ~2",
    "BGE ~2, <C>, <B>",
    "JMP <A>",
    "NOP"
  ],
  "BOD": [
    "@^",
    "AND ^1, <B>, 1",
    "BGE <A>, ^1, 1",
    "@V"
  ],
  "BEV": [
    "@^",
    "AND ^1, <B>, 1",
    "BGE ~3, ^1, 1",
    "@V",
    "JMP <A>",
    "NOP"
  ],
  "BLE": [
    "BGE <A>, <C>, <B>"
  ],
  "BRZ": [
    "BGE ~2, <B>, 1",
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
    "BGE ~2, <B>, &1(0)",
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
    "PSH .return_addr",
    "JMP <A>",
    ".return_addr",
    "NOP"
  ],
  "RET": [
    "@^",
    "POP ^1",
    "JMP ^1",
    "@V"
  ],
  "HLT": [
    ".HLT",
    "JMP .HLT"
  ],
  "CPY": [
    "@^",
    "LOD ^1, <B>",
    "STR <A>, ^1",
    "@V",
  ],
  "BRC": [
    "@^",
    "ADD ^1, <B>, <C>",
    "BRL <A>, ^1, <B>",
    "BRL <A>, ^1, <C>",
    "@V"
  ],
  "BNC": [
    "@^",
    "ADD ^1, <B>, <C>",
    "BRL ~2, ^1, <B>",
    "BGE <A>, ^1, <C>",
    "@V"
  ],
  # COMPLEX TRANSLATIONS
  "MLT": [ # IMPROVED
    "@^",
    "MOV ^1, <C>",
    "@^",
    "MOV ^2, <B>",
    "IMM <A>, 0",
    "BRZ ~6, ^1",
    "DEC ^1, ^1",
    "ADD <A>, <A>, ^2",
    "BNZ ~-2, ^1",
    "@V",
    "@V",
    "NOP"
  ],
  "DIV": [ # IMPROVED
    "IMM <A>, 0",
    "BRL ~10, <B>, <C>",
    "@^",
    "MOV ^1, <B>",
    "@^",
    "MOV ^2, <C>",
    "INC <A>, <A>",
    "SUB ^1, ^1, ^2",
    "BGE ~-2, ^1, ^2",
    "@V",
    "@V",
    "NOP"
  ],
  "MOD": [
    "@^",
    "MOV ^1, <C>",
    "MOV <A>, <B>",
    "BRL ~4, <A>, ^1",
    "SUB <A>, <A>, ^1",
    "JMP ~-2",
    "@V",
    "NOP"
  ],
  "BSR": [
    "@^",
    "MOV ^1, <C>",
    "MOV <A>, <B>",
    "BRZ ~5, ^1",
    "RSH <A>, <A>",
    "DEC ^1, ^1",
    "JMP ~-3",
    "@V",
    "NOP"
  ],
  "BSL": [
    "@^",
    "MOV ^1, <C>",
    "MOV <A>, <B>",
    "BRZ ~5, ^1",
    "LSH <A>, <A>",
    "DEC ^1, ^1",
    "JMP ~-3",
    "@V",
    "NOP"
  ],
  "SRS": [
    "BRN ~3, <B>",
    "RSH <A>, <B>",
    "JMP ~3",
    "RSH <A>, <B>",
    "ADD <A>, <A>, &1(0)",
    "NOP"
  ],
  "BSS": [
    "@^",
    "MOV ^1, <C>",
    "MOV <A>, <B>",
    "BRZ ~5, ^1",
    "SRS <A>, <A>",
    "DEC ^1, ^1",
    "JMP ~-3",
    "@V",
    "NOP"
  ],
  "SETE": [ # IMPROVED
    "BNE ~3, <B>, <C>",
    "IMM <A>, &(1)",
    "JMP ~2",
    "IMM <A>, 0",
    "NOP"
  ],
  "SETNE": [ # IMPROVED
    "BRE ~3, <B>, <C>",
    "IMM <A>, &(1)",
    "JMP ~2",
    "IMM <A>, 0",
    "NOP"
  ],
  "SETG": [ # IMPROVED
    "BLE ~3, <B>, <C>",
    "IMM <A>, &(1)",
    "JMP ~2",
    "IMM <A>, 0",
    "NOP"
  ],
  "SETL": [ # IMPROVED
    "BGE ~3, <B>, <C>",
    "IMM <A>, &(1)",
    "JMP ~2",
    "IMM <A>, 0",
    "NOP"
  ],
  "SETGE": [ # IMPROVED
    "BRL ~3, <B>, <C>",
    "IMM <A>, &(1)",
    "JMP ~2",
    "IMM <A>, 0",
    "NOP"
  ],
  "SETLE": [ # IMPROVED
    "BRG ~3, <B>, <C>",
    "IMM <A>, &(1)",
    "JMP ~2",
    "IMM <A>, 0",
    "NOP"
  ],
  "SETC": [
    "@^",
    "MOV ^1, <B>",
    "BRG ~2, <B>, <C>",
    "MOV ^1, <C>",
    "ADD <A>, <B>, <C>",
    "SETL <A>, <A>, ^1",
    "@V"
  ],
  "SETNC": [
    "@^",
    "MOV ^1, <B>",
    "BRG ~2, <B>, <C>",
    "MOV ^1, <C>",
    "ADD <A>, <B>, <C>",
    "SETL <A>, <A>, ^1",
    "@V"
  ],
  "LLOD": [
    "ADD <A>, <B>, <C>",
    "LOD <A>, <A>"
  ],
  "LSTR": [
    "@^",
    "ADD ^1, <B>, <C>",
    "STR ^1, <A>",
    "@V"
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
    program = handlePragmas(program)
    program = replaceIncludes(program)
    program = replaceDefines(program)
    program = convertAddresses(program)
    program = replaceDefines(program)
    program = convertToInstructions(program)
    program = convertOperands(program)
    program = fixOperands(program)
    return program

def handlePragmas(program):
    global validPragmas
    global pragmas
    seen = []
    code = []
    for x,line in enumerate(program):
        line = line.split()
        if line[0] == "@PRAGMA":
            opts = line[2:]
            if line[1] in seen:
                print(f"ERROR - DUPLICATE PRAGMA - Directive {line[1]} already set!")
                raise Exception("Compiler error! See compiler log for more information!")
            else:
                seen.append(line[1])
            flags = validPragmas.get(line[1])
            if (flags):
                for option in opts:
                    for i in range(len(flags)):
                        if option in flags[i]:
                            pragmas[line[1]][i] = option
        else:
            code.append(" ".join(line))
    return list(filter(None, code))


def removeComments(program):
    # Removes all comments from the code
    # Changes all registers denoted with R to $
    # Changes all memory addresses denoted with M to #
    # Removes any empty lines
    code = []
    for x, line in enumerate(program):
        if line != None and line[:2] != "//" and line[:1] != ";" and line != "":
            line = line.split("//")[0]
            line = line.split(";")[0]
            line = line.split()
            code.append(" ".join(line))
    return list(filter(None, code))

def replaceIncludes(program):
    # Replaces @INCLUDE <file> macros with the text inside <file>
    code = []
    for x,line in enumerate(program):
        line = line.split()
        if line[0] == "@INCLUDE":
            file = " ".join(line[1:]).strip()
            insert = removeComments([l.strip() for l in open(file, "r", encoding="utf8")])
            for l in insert:
                code.append(l)
        else:
            code.append(" ".join(line))
    return list(filter(None, code))

def replaceDefines(program):
    # Parses @DEFINE macros and replaces
    # Default behavior - Prints a warning and overrides define but DOES NOT throw an error for duplicate defines
    code = []
    defines = [[],[]]
    for x,line in enumerate(program):
        line = line.split()
        if line[0] == "@DEFINE":
            if line[1] in defines[0]:
                match (pragmas["DuplicateDefines"][0]):
                    case "silent":
                        pass

                    case "warning":
                        print(f"WARNING - DUPLICATE DEFINE - {line[1]} is defined more than once")
                        match (pragmas["DuplicateDefines"][1]):
                            case "ignore":
                                print(f"    Keeping old value {defines[1][defines[0].index(line[1])]} and ignoring new value {line[2]}")

                            case "overwrite":
                                print(f"    Overwriting old value {defines[1][defines[0].index(line[1])]} with new value {line[2]}")

                    case "error":
                        print(f"ERROR - DUPLICATE DEFINE - {line[1]} is defined more than once")
                        raise Exception("Compiler error! See compiler log for more information!")

                if (pragmas["DuplicateDefines"][1] == "overwrite"):
                    defines[1][defines[0].index(line[1])] = line[2] 
            else:
                defines[0].append(line[1])
                defines[1].append(line[2])
        else:
            for token in range(len(line)):
                if line[token] in defines[0]:
                    line[token] = defines[1][defines[0].index(line[token])]
            code.append(" ".join(line))
    return list(filter(None, code))

def convertAddresses(program):
    code = []
    for x,line in enumerate(program):
        line = line.split()
        for y, token in enumerate(line):
            if token[0] == "R" and token[1:].rstrip(",").isnumeric():
                line[y] = "$" + token[1:]
            elif token[0] == "M" and token[1:].rstrip(",").isnumeric():
                line[y] = "#" + token[1:]
        code.append(" ".join(line))
    return list(filter(None, code))

def convertToInstructions(program):
    # Converts a whole program to instruction objects
    # Removes any empty lines
    code = []
    labels = []
    for x, ins in enumerate(program):
      insNew = instruction([], "", [])
      insert = []
      ins = ins.split()
      if ins[0][0] == ".":
        labels.append(ins[0][1:])
        continue
      else:
        insNew.opcode = ins[0]
        insNew.label = labels
        insNew.operandList = [y.rstrip(",") for y in ins[1:]]
        if insNew.opcode == "DW" and len(insNew.operandList) > 1:
          if insNew.operandList[0][0] == "[":
            insNew.operandList[0] = insNew.operandList[0][1:]
            insNew.operandList[-1] = insNew.operandList[-1][:-1]
          insert = [instruction([], "DW", [opr.strip(",")]) for opr in insNew.operandList]
        if insNew.opcode == "DW":
          if insNew.operandList[0][0] == '"':
            insNew.operandList[0] = insNew.operandList[0][1:-1]
            insert = [instruction([], "DW", [f"'{c}'"]) for c in insNew.operandList[0]]
      if insert != []:
        insert[0].label = insNew.label
        code += insert
      else:
        code.append(insNew)
      labels = []
    return list(filter(None, code))

def convertOperands(program):
  # Converts all operands to operand objects
  for x, ins in enumerate(program):
    try:
      program[x].opcode = opcode(ins.opcode, *opcodes[ins.opcode])
    except:
      program[x].opcode = opcode(ins.opcode, "unknown", "unknown")
    for y, lab in enumerate(program[x].label):
      program[x].label[y] = operand("label", lab)
    for y, opr in enumerate(program[x].operandList):
      if "[" in opr and opr != '"["' and opr != "'['":
        opr, word = opr.split("[")
        word = int(word.rstrip("]"))
      else:
        word = 0
      if opr[0] == "$":
        ins.operandList[y] = operand("register", int(opr[1:]), word)
      elif opr[0] == "#":
        ins.operandList[y] = operand("memAddr", int(opr[1:]), word)
      elif opr[0] == ".":
        ins.operandList[y] = operand("label", opr[1:], word)
      elif opr[0] == "~":
        ins.operandList[y] = operand("relativeAddr", int(opr[1:]), word)
      elif opr == "SP":
        ins.operandList[y] = operand("stackPtr", "", word)
      elif opr[0] in "&@" and opr[1:] in ("MSB","LSB","BITS","SMSB","MAX","SMAX","UHALF","LHALF","MINREG","MINRAM","MINHEAP","MINSTACK"):
        ins.operandList[y] = operand("bitPattern", opr[1:], word)
      elif opr[0] == "%":
        ins.operandList[y] = operand("port", opr[1:], word)
      elif opr[0] == "<" and ins.opcode.type != "header":
        ins.operandList[y] = operand("placeholder", opr[1], word)
      elif opr[0] == "^":
        ins.operandList[y] = operand("tempreg", int(opr[1:]), word)
      elif opr[0] in ('"',"'"):
        o = opr[1:][:-1]
        if o == r"\n":
          ins.operandList[y] = operand("number", 10, word)
        elif o == r"\BS":
          ins.operandList[y] = operand("number", 8, word)
        elif o == r"\SP":
          ins.operandList[y] = operand("number", 32, word)
        elif o == r"\LF":
          ins.operandList[y] = operand("number", 10, word)
        elif o == r"\CR":
          ins.operandList[y] = operand("number", 13, word)
        else:
          ins.operandList[y] = operand("number", ord(o), word)
      else:
        try:
          ins.operandList[y] = operand("number", int(opr, 0), word)
        except:
          if len(opr) == 1:
            ins.operandList[y] = operand("number", ord(opr), word)
          else:
            ins.operandList[y] = operand("other", opr, word)
  return program

def readHeaders(program):
  # Reads and removes the program headers
  global MINRAM
  global MINREG
  global MINSTACK
  global MAXREG
  global IMPORTS
  global PROGBITS
  global BITS
  global MWADDR
  global MWLABEL
  global MWSP
  global MWFULL
  global NEXT
  done = False
  while not done:
    done = True
    for x, ins in enumerate(program):
      for y, opr in enumerate(ins.operandList):
        if opr.type == "register":
          if opr.value > MAXREG:
            MAXREG = opr.value
      if ins.opcode.type in ("header", "pragma"):
        if ins.opcode.name in ("MINRAM", "MINHEAP"):
          MINRAM = ins.operandList[0].value
        elif ins.opcode.name == "MINSTACK":
          MINSTACK = ins.operandList[0].value
        elif ins.opcode.name == "MINREG":
          MINREG = ins.operandList[0].value
        elif ins.opcode.name == "BITS":
          PROGBITS = ins.operandList[1].value
        elif ins.opcode.name == "@NEXT":
          NEXT = True
        elif ins.opcode.name == "@MWADDR":
          MWADDR = True
        elif ins.opcode.name == "@MWLABEL":
          MWLABEL = True
        elif ins.opcode.name == "@MWSP":
          MWSP = True
        elif ins.opcode.name == "@MWFULL":
          if BITS < PROGBITS:
            MWFULL = True
          else:
            MWFULL = False
        else:
          continue
        done = False
        program.pop(x)
        break
  return program

def evaluateBitPattern(bitPattern):
  global BITS
  global MINREG
  global MINRAM
  global MINSTACK
  # Converts operand objects of type "bitPattern" to operand objects of type "number"
  # Allows bit patterns in the form &(1)(0)+c where c is a constant
  opr = bitPattern.value
  c = 0
  if opr == "MAX":
    opr = "(1)"
  elif opr == "MSB":
    opr = "1(0)"
  elif opr == "SMSB":
    opr = "01(0)"
  elif opr == "SMAX":
    opr = "0(1)"
  elif opr == "UHALF":
    opr = "(1)(0)"
  elif opr == "LHALF":
    opr = "(0)(1)"
  elif opr == "BITS":
    return operand("number", BITS)
  elif opr == "MINREG":
    return operand("number", MINREG)
  elif opr == "MINRAM" or opr == "MINHEAP":
    return operand("number", MINRAM)
  elif opr == "MINSTACK":
    return operand("number", MINSTACK)
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
  done = False
  for segment in pattern:
    segments.append(segment)
    segmentString = "".join(segments)
    if segmentString.count("0") + segmentString.count("1") == BITS:
      done = True
      break
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
    if "[" in opr:
      opr, word = opr.split("[")
      word = int(word.rstrip("]"))
    else:
      word = 0
    if opr[0] == "$":
      ins.operandList[y] = operand("register", int(opr[1:]), word)
    elif opr[0] == "#":
      ins.operandList[y] = operand("memAddr", int(opr[1:]), word)
    elif opr[0] == ".":
      ins.operandList[y] = operand("label", opr[1:], word)
    elif opr[0] == "~":
      ins.operandList[y] = operand("relativeAddr", int(opr[1:]), word)
    elif opr == "SP":
      ins.operandList[y] = operand("stackPtr", "", word)
    elif opr[0] in "&@" and opr[1:] in ("MSB","LSB","BITS","SMSB","MAX","SMAX","UHALF","LHALF","MINREG","MINRAM","MINHEAP","MINSTACK"):
      ins.operandList[y] = operand("bitPattern", opr[1:], word)
    elif opr[0] == "%":
      ins.operandList[y] = operand("port", opr[1:], word)
    elif opr[0] == "<" and ins.opcode.type != "header":
      ins.operandList[y] = operand("placeholder", opr[1], word)
    elif opr[0] == "^":
      ins.operandList[y] = operand("tempreg", int(opr[1:]), word)
    elif opr[0] in ('"',"'"):
      o = opr[1:][:-1]
      if o == r"\n":
        ins.operandList[y] = operand("number", 10, word)
      elif o == r"\BS":
        ins.operandList[y] = operand("number", 8, word)
      elif o == r"\SP":
        ins.operandList[y] = operand("number", 32, word)
      elif o == r"\LF":
        ins.operandList[y] = operand("number", 10, word)
      elif o == r"\CR":
        ins.operandList[y] = operand("number", 13, word)
      else:
        ins.operandList[y] = operand("number", ord(opr[1]), word)
    else:
      try:
        ins.operandList[y] = operand("number", int(opr, 0), word)
      except:
        if len(opr) == 1:
          ins.operandList[y] = operand("number", ord(opr), word)
        else:
          ins.operandList[y] = operand("other", opr, word)
  return ins

def replaceComplex(program):
  # Replaces unsupported instructions with lower-level translations where possible
  # Uses tempregs where necessary
  global labelCount
  global MAXTEMPREG
  global DEPTH
  global POINTERS
  global WORDS
  global BITS
  global TEMPREGPTR
  global MWLABEL
  global MWFULL
  global MWFULL_flag
  global ptrs
  done = False
  alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
  translationList = [
    "ADD",
    "NOR",
    "OR",
    "AND",
    "NAND",
    "XOR",
    "XNOR",
    "NOT",
    "RSH",
    "BGE",
    "STR",
    "LOD",
    "IMM",
    "JMP",
    "BRL",
    "BRG",
    "BLE",
    "BNE",
    "BRE",
    "BRZ",
    "BNZ",
    "BRN",
    "BRP",
    "INC",
    "DEC",
    "HLT"
    ]
  pickup = 0
  tempregptr = 0
  while not done:
    done = True
    ptrs = []
    for x in range(pickup, len(program)):
      ins = program[x]
      if ins.opcode.name == "@PTR":
        ptrs.append((ins.operandList[0].type, ins.operandList[0].value))
        continue
      elif ins.opcode.name == "@UNPTR":
        ptrs.remove((ins.operandList[0].type, ins.operandList[0].value))
        continue
      elif ins.opcode.name == "@^":
        tempregptr += 1
      elif ins.opcode.name == "@V":
        tempregptr -= 1
      if (ISA.Instruction_table.get(ins.opcode.name) == None and ISA.Instruction_table.get(getOperandStructure(ins)) == None and not (MWFULL_flag and MWFULL) and not ISA.__name__ == "ISA_configs.Complex") or (MWFULL_flag and MWFULL and ins.opcode.name not in translationList):
        if "MW_" in ins.opcode.name:
          continue
        if "MULTI_" in ins.opcode.name:
          translation = []
          opc = ins.opcode.name[6:]
          # These will do the appropriate operations on multi-word registers
          if opc == "INC":
            translation += ["MULTI_MOV <A>, <B>"]
            for w in range(WORDS):
              translation += [
                f"INC <A>[{w}], <A>[{w}]",
                f"BNZ .end, <A>[{w}]",
              ]
            translation = translation[:-1]
            translation += [".end", "NOP"]
          elif opc == "DEC":
            translation += ["MULTI_MOV <A>, <B>"]
            for w in range(WORDS):
              translation += [
                f"DEC <A>[{w}], <A>[{w}]",
                f"BNE .end, <A>[{w}], &(1)",
              ]
            translation = translation[:-1]
            translation += [".end", "NOP"]
          elif opc == "ADD":
            translation += [
              "MULTI_MOV <A>, <B>",
              "BRC .skip, <A>, <C>",
              "ADD <A>, <A>, <C>",
              "JMP .end",
              ".skip",
              "ADD <A>, <A>, <C>"
            ]
            for w in range(1, WORDS):
              translation += [
                f"INC <A>[{w}], <A>[{w}]",
                f"BNZ .end, <A>[{w}]",
              ]
            translation = translation[:-1]
            translation += [".end", "NOP"]
          elif opc == "MULTI_ADD":
            translation += ["@^", "IMM ^1, 0"]
            for w in range(1, WORDS):
              translation += [
                f"BRZ .skipinc{w}, ^1",
                f"INC <A>[{w}], <A>[{w}]",
                f"SETNE ^1, <A>, 0",
                f".skipinc{w}",
                f"ADD <A>[{w}], <A>[{w}], <B>[{w}]",
                f"BRL .skipset{w}, <B>[{w}], <A>[{w}]",
                f"IMM ^1, &(1)",
                f".skipset{w}",
              ]
            translation += ["@V"]
          elif opc == "MULTI_SUB":
            translation += ["@^", "IMM ^1, 0"]
            for w in range(1, WORDS):
              translation += [
                f"BRZ .skipdec{w}, ^1",
                f"DEC <A>[{w}], <A>[{w}]",
                f"SETNE ^1, <A>, &(1)",
                f".skipdec{w}",
                f"@^",
                f"SUB ^2, <A>[{w}], <B>[{w}]",
                f"BLE .skipset{w}, ^2, <A>[{w}]",
                f"@V",
                f"IMM ^1, &(1)",
                f".skipset{w}",
                f"SUB <A>[{w}], <A>[{w}], <B>[{w}]"
              ]
            translation += ["@V"]
          elif opc == "SUB":
            translation += [
              "MULTI_MOV <A>, <B>",
              "NEG <C>, <C>",
              "BNC .skip, <A>, <C>",
              "NEG <C>, <C>",
              "SUB <A>, <A>, <C>",
              "JMP .end",
              ".skip",
              "NEG <C>, <C>",
              "SUB <A>, <A>, <C>",
            ]
            for w in range(1, WORDS):
              translation += [
                f"DEC <A>[{w}], <A>[{w}]",
                f"BNE .end, <A>[{w}], &(1)",
              ]
            translation = translation[:-1]
            translation += [".end", "NOP"]
          elif opc == "LLOD":
            if (ins.operandList[0].type, ins.operandList[0].value) in ptrs:
              translation += [
                "@^",
                "@PTR ^1",
                "MULTI_ADD ^1, <B>, <C>",
                "MULTI_LOD <A>, ^1",
                "@UNPTR ^1",
                "@V"
              ]
            else:
              translation += [
                "@^",
                "@PTR ^1",
                "MULTI_ADD ^1, <B>, <C>",
                "LOD <A>, ^1",
                "@UNPTR ^1",
                "@V"
              ]
          elif opc == "LSTR":
            if (ins.operandList[0].type, ins.operandList[0].value) in ptrs:
              translation += [
                "@^",
                "@PTR ^1",
                "MULTI_ADD ^1, <B>, <C>",
                "MULTI_STR ^1, <A>",
                "@UNPTR ^1",
                "@V"
              ]
            else:
              translation += [
                "@^",
                "@PTR ^1",
                "MULTI_ADD ^1, <B>, <C>",
                "STR ^1, <A>",
                "@UNPTR ^1",
                "@V",
              ]
          elif opc == "LOD":
            if ins.operandList[0].equals(ins.operandList[1]):
              translation += ["@^","@PTR ^1"]
              target = "^1"
            else:
              target = "<A>"
            for w in range(WORDS):
              translation += [
                f"LOD {target}[{w}], <B>",
                f"MULTI_MULTI_ADD <B>, {MINRAM}",
              ]
            translation += [f"MULTI_MULTI_SUB <B>, {MINRAM*WORDS}"]
            if ins.operandList[0].equals(ins.operandList[1]):
              translation += ["MULTI_MOV <A>, ^1","@UNPTR ^1","@V"]
          elif opc == "STR":
            for w in range(WORDS):
              translation += [
                f"STR <A>, <B>[{w}]",
                f"MULTI_MULTI_ADD <A>, {MINRAM}",
              ]
            translation += [f"MULTI_MULTI_SUB <A>, {MINRAM*WORDS}"]
          elif opc in ("MOV", "IMM"):
            for w in range(WORDS):
              translation.append(f"{opc} <A>[{w}], <B>[{w}]")
        else:
          translation = []
          if ins.opcode.name in ("CAL", "RET") and MWLABEL:
            if ins.opcode.name == "CAL":
              for w in range(WORDS):
                translation += [
                  f"PSH .ret[{w}]",
                ]
              translation += [
                "JMP <A>",
                ".ret",
                "NOP"
              ]
            if ins.opcode.name == "RET":
              translation += [
                "@^",
                "@PTR ^1"
              ]
              for w in range(WORDS):
                translation += [
                  f"POP ^1[{WORDS-1-w}]"
                ]
              translation += [
                "JMP ^1",
                "@UNPTR ^1",
                "@V"
              ]
          elif cmplx_subs.get(getOperandStructure(ins)) == None or ins.opcode.name == "NOP":
            if cmplx_subs.get(ins.opcode.name) == None or ins.opcode.name == "NOP":
              continue
            else:
              translation = copy.deepcopy(cmplx_subs.get(ins.opcode.name))
          else:
            translation = copy.deepcopy(cmplx_subs.get(getOperandStructure(ins)))
        lab = copy.deepcopy(ins.label)
        done = False
        if translation != None:
          translation = parseURCL(translation)
          if not MWFULL:
            translation = regSubstitution(translation)
          translation = replaceComplex(copy.deepcopy(translation))
          for z, tins in enumerate(translation):
            for w, tlab in enumerate(tins.label):
              if tlab.value != "":
                translation[z].label[w].value = tlab.value + f"__{labelCount}"
            for w, topr in enumerate(tins.operandList):
              if topr.type == "tempreg":
                topr.value += tempregptr
              elif topr.type == "label":
                topr.value = topr.value + f"__{labelCount}"
          for z, tins in enumerate(translation):
            for w, topr in enumerate(tins.operandList):
              if topr.type == "placeholder":
                i = alphabet.index(topr.value)
                topr.type = ins.operandList[i].type
                topr.value = ins.operandList[i].value
                if topr.word == 0:
                  topr.word = ins.operandList[i].word
          TEMPREGPTR = tempregptr
          DEPTH += 1
        else:
          print(f"Cannot translate:\n  - No URCL or ISA translations are available for {ins.opcode.name}.\nFull instruction:")
          printIns(ins)
          input()
          s.exit()
        program = program[:x] + translation + program[x+1:]
        program[x].label += lab
        labelCount += 1
        pickup = x
      else:
        continue
      break
  return program

def printIns(ins):
  # Prints a single URCL instruction, with labels
  for lab in ins.label:
    if lab.word == 0:
      print("." + lab.value)
    else:
      print("." + lab.value + f"[{lab.word}]")
  print(ins.opcode.name + " " + ", ".join([prefixes.get(opr.type, "") + str(opr.value) if opr.word == 0 else prefixes.get(opr.type, "") + str(opr.value) + f"[{opr.word}]" for opr in ins.operandList]))
  return

def regSubstitution(program):
  # Replaces unsupported operand structures with register-only versions
  # Example: ADD $1, $2, 15   ->   IMM $3, 15; ADD $1, $2, $3
  global MAXREG
  global MAXTEMPREG
  global TEMPREGPTR
  global MWLABEL
  global WORDS
  global FINALSUB
  exempt = ("IMM", "header", "pragma", "IN", "MULTI_IMM", "MULTI_MULTI_ADD", "MULTI_MULTI_SUB", "DW")
  x = -1
  Instruction_table = ISA.Instruction_table
  name = ISA.__name__
  CPU_stats = ISA.CPU_stats
  tempregptr = 0
  while x < len(program)-1:
    x += 1
    ins = program[x]
    if ins.opcode.name == "@^":
      tempregptr += 1
      continue
    elif ins.opcode.name == "@V":
      tempregptr -= 1
      continue
    newOpcode = getOperandStructure(ins)
    if (Instruction_table.get(ins.opcode.name) or ("_" in ins.opcode.name and ins.opcode.name[0].isnumeric())) and name in ("ISA_configs.Core","ISA_configs.Basic","ISA_configs.Complex"):
      if not CPU_stats["REG_ONLY"]:
        continue
    if Instruction_table.get(newOpcode) == None and ins.opcode.name not in exempt and ins.opcode.type not in exempt:
      if ("IN" in ins.opcode.name and ins.opcode.type == "other"):
        continue
      swap = []
      hit = False
      insert = []
      lab = []
      postinsert = []
      for y, opr in enumerate(program[x].operandList):
        if opr.type not in ("register", "stackPtr", "tempreg", "placeholder") and ins.operandList != [] and not (y == 0 and (ins.opcode.name in "OUT" or ("OUT" in ins.opcode.name and ins.opcode.type == "other"))):
          if opr.type == "label" and y == 0 and ins.opcode.type == "branch" and MWLABEL and WORDS > 1 and not FINALSUB:
            continue
          if not hit:
            lab = program[x].label
            program[x].label = []
            hit = True
          if opr not in swap:
            swap.append(opr)
          for s, val in enumerate(swap):
            if opr.equals(val):
              insert += [
                  instruction([], opcode("@^", "pragma", "other"), []),
                  instruction([], opcode("IMM", "register", "core"), [operand("tempreg", s+1+tempregptr), operand(val.type, val.value, val.word)]),
                ]
              postinsert.append(instruction([], opcode("@V", "pragma", "other"), []))
              program[x].operandList[y] = operand("tempreg", s+1+tempregptr)
      if hit:
        program = program[:x] + insert + [program[x]] + postinsert + program[x+1:]
        program[x].label = lab
        x += len(insert) + len(postinsert)
      continue
  return program

def replaceTempReg(program):
  # Turns tempregs into real registers
  global MAXREG
  global WORDS
  global POINTERS
  global MWADDR
  global MWSP
  global MWFULL
  global ptrs
  maxptr = 0
  for x, ins in enumerate(program):
    if ins.opcode.name == "@PTR":
      ptrs.append((ins.operandList[0].type, ins.operandList[0].value))
    elif ins.opcode.name == "@UNPTR":
      ptrs.remove((ins.operandList[0].type, ins.operandList[0].value))
    if len(ptrs) > maxptr:
      maxptr = len(ptrs)
  tempmaxtempreg = 0
  for x, ins in enumerate(program):
    for y, opr in enumerate(ins.operandList):
      if opr.type == "tempreg" and opr.value > tempmaxtempreg:
        tempmaxtempreg = opr.value
  for x, ins in enumerate(program):
    for y, opr in enumerate(program[x].operandList):
      if opr.type == "tempreg":
        program[x].operandList[y].type = "register"
        program[x].operandList[y].value += MAXREG
  MAXREG = 0
  for x, ins in enumerate(program):
    for y, opr in enumerate(ins.operandList):
      if opr.type == "register":
        if opr.value > MAXREG:
          MAXREG = opr.value
  if WORDS > 1:
    regList = [x for x in range(1, 1+(WORDS-1)*100)]
    pointerList = [regList[(WORDS-1)*x:(WORDS-1)*(x+1)] for x in range(int(len(regList)/(WORDS-1)))]
  for x, ins in enumerate(program):
    if ins.opcode.name == "@PTR":
      ptrs.append((ins.operandList[0].type, ins.operandList[0].value))
    elif ins.opcode.name == "@UNPTR":
      ptrs.remove((ins.operandList[0].type, ins.operandList[0].value))
    for y, opr in enumerate(program[x].operandList):
      if opr.type == "register" and opr.word > 0:
        if opr.value == 0:
          opr.word = 0
        elif MWFULL:
          tregs = copy.deepcopy(pointerList[opr.value])
          program[x].operandList[y] = operand("tempreg", tregs[opr.word-1])
        else:
          val = (opr.type, opr.value)
          tregs = copy.deepcopy(pointerList[ptrs.index(val)])
          program[x].operandList[y] = operand("tempreg", tregs[opr.word-1])
        program[x].operandList[y].word = 0
        opr = program[x].operandList[y]
      if opr.type == "stackPtr" and opr.word > 0 and (MWSP or MWFULL):
        tregs = copy.deepcopy(pointerList[maxptr])
        program[x].operandList[y] = operand("tempreg", tregs[opr.word-1])
        opr = program[x].operandList[y]
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
    if opr.type in ("register", "tempreg", "stackPtr", "placeholder"):
        tag += "r"
    else:
        tag += "i"
  if tag == "r"*len(tag):
    return ins.opcode.name
  else:
    return ins.opcode.name + "_" + tag

def optimise(program):
  # Performs basic optimisations:
  # - removes NOP
  # - removes MOV <A>, <A>
  # - changes MOV reg, imm to IMM reg, imm
  # - strips any pragmas
  # - evaluates multi-word numbers
  global WORDS
  global BITS
  snip = False
  for x, ins in enumerate(program):
    if ins.opcode.name in ("NOP", "@PTR", "@UNPTR", "@^", "@V", "MW_NOP"):
      snip = True
    elif ins.opcode.name == "MOV" and ins.operandList[0].equals(ins.operandList[1]):
      snip = True
    elif ins.opcode.name == "MOV" and ins.operandList[1].type not in ("register", "stackPtr", "tempreg"):
      program[x].opcode.name = "IMM"
    elif ins.opcode.name == "ADD" and ins.operandList[2].type == "register" and ins.operandList[2].value == 0 and ins.operandList[0].equals(ins.operandList[1]):
      snip = True
    if snip:
      snip = False
      if x == len(program)-1:
        program = program[:-1]
        break
      program[x+1].label += copy.deepcopy(program[x].label)
      program[x] = None
    for y, opr in enumerate(ins.operandList):
      if opr.type == "number":
        opr.value = (opr.value >> (BITS*opr.word)) & ((2**BITS)-1)
        opr.word = 0
  program = list(filter(None, program))
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
          print(f"Cannot translate:\n  - No URCL or ISA translations are available for {ins.opcode.name}.\nFull instruction:")
          printIns(ins)
          input()
    for t, tins in enumerate(translation):
      translation[t] = ISAinstruction([], translation[t])
      if t == 0:
        translation[t].label = [f".{lbl.value}%" for lbl in ins.label]
      for o, opr in enumerate(ins.operandList):
        if opr.type not in ("label", "memAddr"):
          translation[t].instruction = translation[t].instruction.replace(f"<{alphabet[o]}>", prefixes.get(opr.type, "") + str(opr.value))
        else:
          translation[t].instruction = translation[t].instruction.replace(f"<{alphabet[o]}>", prefixes.get(opr.type, "") + str(opr.value) + "^" + str(opr.word) + "%")
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

def setupStack(program):
  global MAXREG
  global MWSP
  global WORDS
  global BITS
  global MWFULL
  newSP = int(ISA.CPU_stats["SP_LOCATION"])
  if newSP == 0:
    newSP = MAXREG + 1
  val = int(ISA.CPU_stats["SP_VALUE"])
  if MWSP or MWFULL:
    for w in range(WORDS):
      program = [instruction([], opcode("IMM", "register", "core"), [operand("stackPtr", "", w), operand("number", (val>>BITS*w)&(2**BITS-1))])] + program
  else:
    program = [instruction([], opcode("IMM", "register", "core"), [operand("stackPtr", ""), operand("number", val)])] + program
  return program

def fixStack(program):
  # Flips the stack if necessary, and prunes "SP" if necessary
  global MAXREG
  global MWSP
  global WORDS
  global BITS
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
  global PROGBITS
  PROGBITS = 8
  global WORDS
  WORDS = 1
  global POINTERS
  POINTERS = []
  global MWADDR
  MWADDR = False
  global MWLABEL
  MWLABEL = False
  global MWSP
  MWSP = False
  global ptrs
  ptrs = []
  global TEMPREGPTR
  TEMPREGPTR = 0
  global FINALSUB
  FINALSUB = False
  global MWFULL
  MWFULL = False
  global MWFULL_flag
  MWFULL_flag = True
  global NEXT
  NEXT = False
  return

def removeISALabels(program):
  global BITS
  # Removes labels from ISA code
  labels = {}
  for x, ins in enumerate(program):
    for lbl in ins.label:
      labels[lbl] = x
    program[x].label = []
  for x, ins in enumerate(program):
    for lbl in labels:
      while lbl[:-1]+"^" in ins.instruction:
        word = int(ins.instruction.split(lbl[:-1])[1].split("^")[1].split("%")[0])
        full_lbl = f"{lbl[:-1]}^{word}%"
        val = (labels[lbl] >> BITS*word) & (2**BITS-1)
        program[x].instruction = program[x].instruction.replace(full_lbl, str(val))
  return program

def shiftRAM(program):
  global RUNRAM
  global BITS
  # Shifts memory addresses in ISA code
  for x, ins in enumerate(program):
    ins = ins.instruction.split()
    for o, opr in enumerate(ins):
      if opr[0] == "#":
        opr = opr[1:]
        excess = ""
        if opr[-1] != "%":
          excess = opr.split("%")[1]
        newopr = opr
        if "^" in opr:
          word = int(opr.split("^")[1].split("%")[0])
          opr = int(opr.split("^")[0])
          newopr = (opr >> BITS*word) & (2**BITS-1)
        if RUNRAM:
          ins[o] = f"{newopr+len(program)}" + excess
        else:
          ins[o] = f"{newopr}" + excess
        program[x].instruction = " ".join(ins)
  return program

def fixPorts(program):
  # Replaces %PORTs with constants
  for x, ins in enumerate(program):
    for y, opr in enumerate(program[x].operandList):
      if opr.type == "port":
        program[x].operandList[y] = operand("number", ISA.Port_table.get("%" + opr.value))
  return program

def enableMultiWord(program):
  global BITS # ISA bits
  global PROGBITS # Program's bits
  global WORDS
  global POINTERS
  global MAXTEMPREG
  global STACKUSAGE
  global MWADDR
  global MWLABEL
  global MWSP
  wordCount = 1

  if BITS < PROGBITS:
    wordCount = math.ceil(PROGBITS / BITS)
  WORDS = wordCount
  if WORDS == 1:
    return program
  if MWADDR:
    for x, ins in enumerate(program):
      if ins.opcode.name == "@PTR":
        ptrs.append((ins.operandList[0].type, ins.operandList[0].value))
        continue
      elif ins.opcode.name == "@UNPTR":
        ptrs.remove((ins.operandList[0].type, ins.operandList[0].value))
        continue
      for y, opr in enumerate(ins.operandList):
        if (opr.type, opr.value) in ptrs or (opr.type == "stackPtr" and MWSP) or opr.type == "memAddr":
          if ins.opcode.name not in ("LOD", "STR"):
            if ins.opcode.name == "ADD" and ((ins.operandList[2].type, ins.operandList[2].value) in ptrs or (ins.operandList[2].type == "stackPtr" and MWSP) or ins.operandList[2].type == "memAddr"):
              temp = ins.operandList[2]
              ins.operandList[2] = ins.operandList[1]
              ins.operandList[1] = temp
            ins.opcode.name = "MULTI_" + ins.opcode.name
            break
      if ins.opcode.name in ("STR") and ((ins.operandList[1].type, ins.operandList[1].value) in ptrs or (opr.type == "stackPtr" and MWSP) or ins.operandList[1].type == "memAddr"):
        ins.opcode.name = "MULTI_" + ins.opcode.name
      elif ins.opcode.name in ("LOD") and ((ins.operandList[0].type, ins.operandList[0].value) in ptrs or (opr.type == "stackPtr" and MWSP) or ins.operandList[0].type == "memAddr"):
        ins.opcode.name = "MULTI_" + ins.opcode.name
  return program

def convertMultiWordInstructions(program):
  global WORDS
  if WORDS == 1:
    return program
  global BITS
  global POINTERS
  global MWADDR
  global MWLABEL
  ptrs = []
  for x, ins in enumerate(program):
    if ins.opcode.name == "@PTR":
      ptrs.append((ins.operandList[0].type, ins.operandList[0].value))
      continue
    elif ins.opcode.name == "@UNPTR":
      ptrs.remove((ins.operandList[0].type, ins.operandList[0].value))
      continue
    # JMPs automatically become DBLE_JMPs, or TRPL_JMPs, or QUAD_JMPs etc. including CAL and RET.
    if MWLABEL:
      if f"{WORDS}_" in ins.opcode.name:
        pass
      elif ins.opcode.name in ("RET"):
        ins.opcode.name = f"{WORDS}_" + ins.opcode.name
      elif ins.opcode.type == "branch":
        if len(ins.operandList) > 1:
          ins.operandList = [operand(ins.operandList[0].type, ins.operandList[0].value, WORDS-y-1) for y in range(WORDS)] + ins.operandList[1:]
        else:
          ins.operandList = [operand(ins.operandList[0].type, ins.operandList[0].value, WORDS-y-1) for y in range(WORDS)]
        ins.opcode.name = f"{WORDS}_" + ins.opcode.name
    # LODs and STRs also automatically become DBLE_LOD, DBLE_STR etc.
    if MWADDR:
      if f"{WORDS}_" in ins.opcode.name:
        pass
      elif ins.opcode.name in ("STR", "IN"):
        ins.operandList = [operand(ins.operandList[0].type, ins.operandList[0].value, WORDS-y-1) for y in range(WORDS)] + ins.operandList[1:]
        ins.opcode.name = f"{WORDS}_" + ins.opcode.name
      elif ins.opcode.name in ("LOD", "OUT"):
        ins.operandList = [ins.operandList[0]] + [operand(ins.operandList[1].type, ins.operandList[1].value, WORDS-y-1) for y in range(WORDS)]
        ins.opcode.name = f"{WORDS}_" + ins.opcode.name
      elif ins.opcode.name in ("PSH", "POP"):
        ins.opcode.name = f"{WORDS}_" + ins.opcode.name
  return program

def fullMultiword(program):
  global WORDS
  global MAXREG
  global TEMPREGPTR
  global MWADDR
  global MWLABEL
  global FINALSUB
  global PROGBITS
  global MWFULL
  global MWFULL_flag
  MWFULL_flag = False
  flg = False
  program = regSubstitution(program)
  for x, ins in enumerate(program):
    if ins.opcode.name[0] not in ("@") and ins.opcode.name not in ("IN", "OUT"):
      ins.opcode.name = "MW_" + ins.opcode.name
  program = list(filter(None, program))
  done = False
  pickup = 0
  tempregptr = 0
  while not done:
    done = True
    translation = []
    for x in range(pickup, len(program)):
      ins = program[x]
      if ins.opcode.name == "@^":
        tempregptr += 1
      elif ins.opcode.name == "@V":
        tempregptr -= 1
      elif "MW_" in ins.opcode.name:
        opc = ins.opcode.name[3:]
        # Multiword translations:
        # ---------- CORE
        # IMM - DONE
        # RSH - DONE
        # BGE - DONE
        # NOR - DONE
        # ADD - DONE
        # LOD - DONE
        # STR - DONE
        # ---------- BASIC
        # MOV - DONE
        # BRG - DONE
        # BRL - DONE
        # BLE - DONE
        # BRE - DONE
        # BNE - DONE
        # BRZ - DONE
        # BNZ - DONE
        # BRN - DONE
        # BRP - DONE
        # JMP - DONE
        # HLT - DONE
        # BRC - TODO
        # BNC - TODO
        # SUB - NOT NEEDED?
        # INC - DONE
        # DEC - DONE
        # LSH - DONE
        # NEG - NOT NEEDED?
        # AND - DONE
        # OR  - DONE
        # XOR - DONE
        # NOT - DONE
        # XNOR- DONE
        # NAND- DONE
        # POP - TODO
        # PSH - TODO
        # CAL - TODO
        # RET - TODO
        if opc == "IMM": # WORKS
          for w in range(WORDS):
            translation += [f"IMM <A>[{w}], <B>[{w}]"]
        elif opc == "INC":
            if not ins.operandList[0].equals(ins.operandList[1]):
              translation.append("MW_MOV <A>, <B>")
            for w in range(WORDS):
              translation += [
                f"INC <A>[{w}], <A>[{w}]",
                f"BNZ .end, <A>[{w}]",
              ]
            translation.pop()
            translation += [".end", "NOP"]
        elif opc == "DEC":
            if not ins.operandList[0].equals(ins.operandList[1]):
              translation.append("MW_MOV <A>, <B>")
            for w in range(WORDS):
              translation += [
                f"DEC <A>[{w}], <A>[{w}]",
                f"BNE .end, <A>[{w}], &(1)",
              ]
            translation.pop()
            translation += [".end", "NOP"]
        elif opc == "MOV": # WORKS
          if not ins.operandList[0].equals(ins.operandList[1]):
            for w in range(WORDS):
              translation += [f"MOV <A>[{w}], <B>[{w}]"]
          else:
            translation += ["NOP"]
        elif opc == "BGE": # WORKS
          if ins.operandList[1].equals(ins.operandList[2]) or ins.operandList[2].value == 0:
            translation += ["BGE <A>, $0, $0"]
          else:
            for w in range(WORDS):
              translation += [
                f"BRL .skip, <B>[{WORDS-w-1}], <C>[{WORDS-w-1}]"
                ]
            translation += [
              f"JMP <A>",
              ".skip",
              "NOP"
              ]
        elif opc == "JMP":
          translation.append("JMP <A>")
        elif opc == "HLT":
          translation.append("HLT")
        elif opc == "BRE":
          if ins.operandList[1].equals(ins.operandList[2]):
            translation += ["JMP <A>"]
          else:
            for w in range(WORDS):
              translation += [
                f"BNE .skip, <B>[{WORDS-w-1}], <C>[{WORDS-w-1}]"
                ]
            translation += [
              f"JMP <A>",
              ".skip",
              "NOP"
              ]
        elif opc == "BRZ":
          for w in range(WORDS):
            translation += [
              f"BNZ .skip, <B>[{WORDS-w-1}]"
              ]
          translation += [
            f"JMP <A>",
            ".skip",
            "NOP"
            ]
        elif opc == "BNZ":
          for w in range(WORDS):
            translation += [
              f"BNZ .exec, <B>[{WORDS-w-1}]"
              ]
          translation += [
              "JMP .skip",
              ".exec",
              "JMP <A>",
              ".skip",
              "NOP"
            ]
        elif opc == "BRN":
          translation += [f"BRN <A>, <B>[{WORDS-1}]"]
        elif opc == "BRP":
          translation += [f"BRP <A>, <B>[{WORDS-1}]"]
        elif opc == "BNE":
          if ins.operandList[1].equals(ins.operandList[2]):
            translation += ["JMP <A>"]
          else:
            for w in range(WORDS):
              translation += [
                f"BNE .exec, <B>[{WORDS-w-1}], <C>[{WORDS-w-1}]"
                ]
            translation += [
              "JMP .skip",
              ".exec",
              "JMP <A>",
              ".skip",
              "NOP"
              ]
        elif opc == "BLE":
          if ins.operandList[1].equals(ins.operandList[2]):
            translation += ["JMP <A>"]
          else:
            for w in range(WORDS):
              translation += [
                f"BRG .skip, <B>[{WORDS-w-1}], <C>[{WORDS-w-1}]"
                ]
            translation += [
              f"JMP <A>",
              ".skip",
              "NOP"
              ]
        elif opc == "BRL":
          if ins.operandList[1].equals(ins.operandList[2]):
            translation += ["NOP"]
          else:
            for w in range(WORDS):
              translation += [
                f"BGE .skip, <B>[{WORDS-w-1}], <C>[{WORDS-w-1}]"
                ]
            translation += [
              f"JMP <A>",
              ".skip",
              "NOP"
              ]
        elif opc == "BRG":
          if ins.operandList[1].equals(ins.operandList[2]):
            translation += ["NOP"]
          else:
            for w in range(WORDS):
              translation += [
                f"BLE .skip, <B>[{WORDS-w-1}], <C>[{WORDS-w-1}]"
                ]
            translation += [
              f"JMP <A>",
              ".skip",
              "NOP"
              ]
        elif opc == "NOR": # WORKS
          for w in range(WORDS):
            translation += [f"NOR <A>[{w}], <B>[{w}], <C>[{w}]"]
        elif opc == "OR": # WORKS
          for w in range(WORDS):
            translation += [f"OR <A>[{w}], <B>[{w}], <C>[{w}]"]
        elif opc == "AND": # WORKS
          for w in range(WORDS):
            translation += [f"AND <A>[{w}], <B>[{w}], <C>[{w}]"]
        elif opc == "NAND": # WORKS
          for w in range(WORDS):
            translation += [f"NAND <A>[{w}], <B>[{w}], <C>[{w}]"]
        elif opc == "XOR": # WORKS
          for w in range(WORDS):
            translation += [f"XOR <A>[{w}], <B>[{w}], <C>[{w}]"]
        elif opc == "XNOR": # WORKS
          for w in range(WORDS):
            translation += [f"XNOR <A>[{w}], <B>[{w}], <C>[{w}]"]
        elif opc == "NOT": # WORKS
          for w in range(WORDS):
            translation += [f"NOT <A>[{w}], <B>[{w}]"]
        elif opc == "LOD": # WORKS
          translation += ["@^", "@^", f"MW_IMM ^1, {MINRAM}", "MW_MOV ^2 <B>"]
          for w in range(WORDS):
            translation += [
              f"LOD <A>[{w}], ^2",
              f"MW_ADD ^2, ^2, ^1",
              ]
          translation.pop()
          translation += [
            "@V",
            "@V"
            ]
        elif opc == "STR": # WORKS
          translation += ["@^", f"MW_MOV ^1, <A>"]
          for w in range(WORDS):
            translation += [
              f"STR ^1, <B>[{w}]",
              f"MW_ADD ^1, ^1, {MINRAM}",
              ]
          translation.pop()
          translation += [
            "@V",
            ]
        elif opc == "ADD": # WORKS
          translation += [
            "@^",
            "IMM ^1, 0",
            "@^",
            "MW_MOV ^2, <C>",
          ]
          if not ins.operandList[0].equals(ins.operandList[1]):
            translation.append("MW_MOV <A>, <B>")
          for w in range(WORDS):
            if w == WORDS-1:
              translation += [
                f"BNZ .skipinc{w}, ^1",
                f"INC <A>[{w}], <A>[{w}]",
                f".skipinc{w}",
                f"ADD <A>[{w}], <A>[{w}], ^2[{w}]",
              ]
            elif w != 0:
              translation += [
                f"BNZ .skipinc{w}, ^1",
                f"INC <A>[{w}], <A>[{w}]",
                f"MOV ^1, <A>[{w}]",
                f".skipinc{w}",
                f"ADD <A>[{w}], <A>[{w}], ^2[{w}]",
                f"SETLE ^2[{w}], ^2[{w}], <A>[{w}]",
                f"OR ^1 ^1 ^2[{w}]"
              ]
            else:
              translation += [
                f"ADD <A>[{w}], <A>[{w}], ^2[{w}]",
                f"SETLE ^2[{w}], ^2[{w}], <A>[{w}]",
                f"OR ^1 ^1 ^2[{w}]",
              ]
          translation += ["@V", "@V"]
        elif opc == "LSH": # WORKS
          translation += [
            "@^", 
            "IMM ^1, 0",
            "@^",
            "IMM ^2, 0"
            ]
          if not ins.operandList[0].equals(ins.operandList[1]):
            translation.append("MW_MOV <A>, <B>")
          for w in range(WORDS):
            if w == WORDS-1:
              translation += [
                f"@V"
                f"BRZ +2 ^1",
                f"IMM ^1 1",
                f"LSH <A>[{w}], <A>[{w}]",
                f"ADD <A>[{w}], <A>[{w}], ^1",
              ]
            elif w != 0:
              translation += [
                f"MOV ^2 ^1",
                f"BRZ +2 ^2",
                f"IMM ^2 1",
                f"AND ^1, <A>[{w}], &1(0)",
                f"LSH <A>[{w}], <A>[{w}]",
                f"ADD <A>[{w}], <A>[{w}], ^2"
              ]
            else:
              translation += [
                f"AND ^1, <A>[{w}], &1(0)",
                f"LSH <A>[{w}], <A>[{w}]",
              ]
          translation += ["@V"]
        elif opc == "RSH": # WORKS
          translation += [
            "@^",
            "IMM ^1, 0",
            "@^",
            "IMM ^2 0"
            ]
          if not ins.operandList[0].equals(ins.operandList[1]):
            translation.append("MW_MOV <A>, <B>")
          for w in range(WORDS):
            if w == WORDS-1:
              translation += [
                f"@V",
                f"BRZ +2 ^1",
                f"IMM ^1 &1(0)",
                f"RSH <A>[{WORDS-1-w}], <A>[{WORDS-1-w}]",
                f"ADD <A>[{WORDS-1-w}], <A>[{WORDS-1-w}], ^1",
              ]
            elif w != 0:
              translation += [
                f"MOV ^2 ^1",
                f"BRZ +2 ^2",
                f"IMM ^2 &1(0)",
                f"AND ^1, <A>[{WORDS-1-w}], 1",
                f"RSH <A>[{WORDS-1-w}], <A>[{WORDS-1-w}]",
                f"ADD <A>[{WORDS-1-w}], <A>[{WORDS-1-w}], ^2",
              ]
            else:
              translation += [
                f"AND ^1, <A>[{WORDS-1-w}], 1",
                f"RSH <A>[{WORDS-1-w}], <A>[{WORDS-1-w}]",
              ]
          translation += ["@V"]
        else:
          continue
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        translation = parseURCL(translation)
        translation = replaceComplex(translation)
        lab = copy.deepcopy(ins.label)
        for z, tins in enumerate(translation):
          for w, tlab in enumerate(tins.label):
            if tlab.value != "":
              translation[z].label[w].value = tlab.value + f"__{labelCount}"
          for w, topr in enumerate(tins.operandList):
            if topr.type == "tempreg":
              topr.value += tempregptr
            elif topr.type == "label":
              topr.value = topr.value + f"__{labelCount}"
        for z, tins in enumerate(translation):
          for w, topr in enumerate(tins.operandList):
            if topr.type == "placeholder":
              i = alphabet.index(topr.value)
              topr.type = ins.operandList[i].type
              topr.value = ins.operandList[i].value
              if topr.word == 0:
                topr.word = ins.operandList[i].word
        TEMPREGPTR = tempregptr
        translation[0].label += lab
        program[x+1:x+1] = translation
        program.pop(x)
        pickup = x
        done = False
        break
  MWADDR = True
  MWLABEL = True
  FINALSUB = True
  program = convertMultiWordInstructions(program)
  program = regSubstitution(program)
  return program

def deflateRegs(program):
  while True:
    regs = []
    for x, ins in enumerate(program):
      for y, opr in enumerate(ins.operandList):
        if opr.type == "register" and opr.value not in regs and opr.value != 0:
          regs.append(opr.value)
    regs = sorted(regs)
    if regs == list(range(1,len(regs)+1)):
      break
    else:
      for r, reg in enumerate(regs):
        if r+1 != reg:
          for x, ins in enumerate(program):
            for y, opr in enumerate(ins.operandList):
              if opr.type == "register" and opr.value > r+1:
                program[x].operandList[y].value -= 1
          break
  return program

def convertOperandsWithHeaders(program):
  global NEXT
  global labelCount
  for x, ins in enumerate(program):
    for y, opr in enumerate(ins.operandList):
      if opr.type == "number" and opr.value < 0:
        if not MWFULL:
          program[x].operandList[y].value = (opr.value)&((2**BITS)-1)
        else:
          program[x].operandList[y].value = (opr.value)&((2**PROGBITS)-1)
      elif opr.type == "label" and NEXT:
        if len(opr.value) < 4:
          continue
        if opr.value[:4] not in ("next","prev"):
          continue
        if len(opr.value) > 4:
          if not opr.value[4:].isnumeric():
            continue
        done = False
        if opr.value[:4] == "next":
          for z, ins2 in enumerate(program[x+1:]):
            if done:
              break
            for l in ins2.label:
              if l.equals(opr):
                program[x + z + 1].label.append(operand("label", f"__label__{labelCount}"))
                program[x].operandList[y] = operand("label", f"__label__{labelCount}")
                labelCount += 1
                done = True
                break
        else:
          rev = program[:x]
          rev.reverse()
          for z, ins2 in enumerate(rev):
            if done:
              break
            for l in ins2.label:
              if l.equals(opr):
                program[x-z-1].label.append(operand("label", f"__label__{labelCount}"))
                program[x].operandList[y] = operand("label", f"__label__{labelCount}")
                labelCount += 1
                done = True
                break
  if NEXT:
    for x, ins in enumerate(program):
      for l, lbl in enumerate(program[x].label):
        if len(lbl.value) < 4:
          continue
        if lbl.value[:4] not in ("next","prev"):
          continue
        if len(lbl.value) > 4:
          if not lbl.value[4:].isnumeric():
            continue
        program[x].label[l] = None
      program[x].label = list(filter(None, program[x].label))
  return program

def removeDW(program):
  count = 0
  # Find out how much memory is going to be required
  for x, ins in enumerate(program):
    if ins.opcode.name == "DW":
      count += 1
  # Free up the required memory slots
  for x, ins in enumerate(program):
    for y, opr in enumerate(program[x].operandList):
      if opr.type == "memAddr":
        program[x].operandList[y].value += count
  # Move the values in 'DW's to memory with 'STR's
  insert = []
  count = 0
  labelDict = {}
  for x, ins in enumerate(program):
    if ins.opcode.name == "DW":
      for lbl in ins.label:
        labelDict[lbl.value] = count
      opr = ins.operandList[0]
      insert.append(f"STR #{count} {prefixes.get(opr.type, '')}{opr.value}")
      count += 1
      program[x] = parseIns("NOP")
  insert = parseURCL(insert)
  program[0:0] = insert
  for x, ins in enumerate(program):
    for y, opr in enumerate(program[x].operandList):
      if opr.type == "label" and labelDict.get(opr.value, None) is not None:
        program[x].operandList[y].type = "memAddr"
        program[x].operandList[y].value = labelDict[opr.value]
  return program

def main():
  global opcodes
  global STACKUSAGE
  global MAXREG
  global MWADDR
  global MWLABEL
  global FINALSUB
  global MWFULL
  global MWFULL_flag
  global WORDS
  if len(s.argv) > 2:
    program = importProgram(s.argv[2])
  else:
    program = importProgram(input("File to compile? (with extension) "))
  program = parseURCL(program)
  try: program, opcodes = ISA.RawURCL(program, opcodes)
  except Exception as ex: end(ex,"- no suggestions, problem with ISA designer's raw URCL tweaks. Report this to them if necessary.")
  program = readHeaders(program)
  program = convertOperandsWithHeaders(program)
  program = enableMultiWord(program)
  program = regSubstitution(program)
  program = replaceComplex(program)
  if ISA.Instruction_table.get("DW", None) == None:
    program = removeDW(program)
  if not MWFULL:
    program = convertMultiWordInstructions(program)
  FINALSUB = True
  if not MWFULL:
    program = regSubstitution(program)
  FINALSUB = False
  checkStackUsage(program)
  MAXREG = 0
  cnt = 0
  for x, ins in enumerate(program):
    if ins.opcode.name == "@^":
      cnt += 1
    elif ins.opcode.name == "@V":
      cnt -= 1
    for y, opr in enumerate(ins.operandList):
      if opr.type == "register":
        if opr.value > MAXREG:
          MAXREG = opr.value
  if MWFULL:
    program = fullMultiword(program)
  if STACKUSAGE:
    program = setupStack(program)
  program = replaceTempReg(program)
  if STACKUSAGE:
    program = fixStack(program)
  program = optimise(program)
  if MWFULL:
    program = deflateRegs(program)
  try: program, opcodes = ISA.CleanURCL(program, opcodes)
  except Exception as ex: end(ex,"- no suggestions, problem with ISA designer's clean  URCL tweaks. Report this to them if necessary.")
  max_y = os.get_terminal_size().lines
  if WORDS > 1 and MWADDR or MWLABEL:
    print(f"MULTI-WORD PATCH APPLIED, WORDS: {WORDS}")
  print(f"\nURCL code:")
  for x, ins in enumerate(program):
    printIns(ins)
    if x > (max_y//2) - 9:
      print(f"... ({len(program)-1-x} more lines)")
      break
  filename = "URCL_output/URCL_output.urcl"
  if len(s.argv) > 4:
      filename = s.argv[4]
  outfile = open(filename, "w+")
  aestheticOutput = True
  for ins in program:
      for lbl in ins.label:
          outfile.write("." + lbl.value + "\n")
      if not ins.opcode.name[0].isnumeric() or not aestheticOutput:
        outfile.write(ins.opcode.name + " " + " ".join([prefixes.get(opr.type, "") + str(opr.value) if opr.word == 0 else prefixes.get(opr.type, "") + str(opr.value) + f"[{opr.word}]" for opr in ins.operandList]) + "\n")
      else:
        ins.opcode.name = ins.opcode.name.split("_")[1]
        outstr = ins.opcode.name + " " + " ".join([prefixes.get(opr.type, "") + str(opr.value) if opr.word == 0 else prefixes.get(opr.type, "") + str(opr.value) + f"[{opr.word}]" for opr in ins.operandList]) + "\n"
        outstr = outstr.split()
        if ins.opcode.type in ("branch") or ins.opcode.name in ("STR","IN"):
          outstr[1] = "[" + outstr[1]
          outstr[WORDS] = outstr[WORDS] + "]"
        else:
          outstr[2] = "[" + outstr[2]
          outstr[WORDS+1] = outstr[WORDS+1] + "]"
        outstr = " ".join(outstr) + "\n"
        outfile.write(outstr)
  outfile.close()
  print(f"URCL code dumped in: {filename}")
  if ISA.__name__ in ("ISA_configs.Emulate","ISA_configs.Core","ISA_configs.Basic","ISA_configs.Complex"):
      return
  program = fixPorts(program)
  program = convertToISA(program)
  try:program = ISA.LabelISA(program)
  except Exception as ex:end(ex,"- no suggestions, problem with ISA designer's labelled ISA tweaks. Report this to them if necessary.")
  if ISA.CPU_stats["REMOVE_LABELS"]:
    program = removeISALabels(program)
  if ISA.CPU_stats["SHIFT_RAM"]:
    program = shiftRAM(program)
  try:program = ISA.FinalISA(program)
  except Exception as ex:end(ex,"- no suggestions, problem with ISA designer's final ISA tweaks. Report this to them if necessary.")
  print(f"\n{ISA.__name__} code:")
  for x, line in enumerate(program):
    if line.label != []:
      print(f"{[lab for lab in line.label]}")
    print(line.instruction)
    if x > (max_y//2) - 9:
        print(f"... ({len(program)-1-x} more lines)")
        break
  filename = f"ISA_output/{ISA.__name__}_output.txt"
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