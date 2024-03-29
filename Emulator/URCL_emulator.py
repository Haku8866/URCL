import sys as s
import os
import colorama
import time
import traceback
import json
from random import randint

operands = {"MINHEAP": 1,"NEG": 2,"DW": 1,"DD": 1,"DQ": 1,"ADD": 3,"SUB": 3,"BSR": 3,"BSL": 3,"ADC": 3,"SBB": 3,"INC": 2,"DEC": 2,"MOV": 2,"IMM": 2,"XOR": 3,"AND": 3,"OR": 3,"NOR": 3,"NAND": 3,"XNOR": 3,"NOT": 2,"LOD": 2,"STR": 2,"JMP": 1,"BRC": 1,"BNC": 1,"BRZ": 1,"BNZ": 1,"BRN": 1,"BRP": 1,"BZR": 2,"BZN": 2,"NOP": 0,"HLT": 0,"MLT": 3,"DIV": 3,"MOD": 3,"SQRT": 2,"CAL": 1,"RET": 0,"PSH": 1,"POP": 1,"BRL": 3,"BRG": 3,"BRE": 3,"BNE": 3,"IN": 2,"OUT": 2,"BOD": 2,"BEV": 2,"RSH": 2,"LSH": 2,"CMP": 2,"SRS": 3,"BSS": 3,"BLE": 3,"BGE": 3,"BITS": 2,"MINREG": 1,"RUN": 1,"MINRAM": 1,"IMPORT": 0,"NAME": 1,"OPS": 1,"REG": 1,"IN": 1,"SETE": 3,"SETNE": 3,"SETG": 3,"SETL": 3,"SETGE": 3,"SETLE": 3,}
RUNRAM = True
databuswidth = 8
PC = 0
CONSOLE = [["█"]]
CONSOLE_X = 0
CONSOLE_Y = 0

PAGE = 0
ADDRESS = 0
FILE = []

class instruction:
  def __init__(self, label, opcode, operandList):
    self.label, self.opcode, self.operandList = label, opcode, operandList
end = (lambda ex, tag: input(f"\n--- Something went wrong :( ---\n\n{ex} {tag}\n") and s.exit())

if os.name == 'nt':
    import msvcrt
    import ctypes
    class _CursorInfo(ctypes.Structure):
        _fields_ = [("size", ctypes.c_int),
                    ("visible", ctypes.c_byte)]

def hide_cursor():
    if os.name == 'nt':
        ci = _CursorInfo()
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
        ci.visible = False
        ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))

def updateFlags(reg):
  global REG
  global BITS
  val = REG[reg]
  val = (val + 2**BITS) % (2**BITS)
  REG[reg] = val
  return

def splitIntoBytes(val):
  global BITS
  words = BITS//8
  if not words:
    words = 1
  out = []
  for w in range(words, 0, -1):
    out.append((val>>((w-1)*8))&(2**8-1))
  return out

def importProgram(name):
  try: return [line.strip() for line in open(name, "r", encoding="utf8")]
  except Exception as ex: end(ex, "- try checking:\n1. Is it in a different folder to URCL_emulator.py?\n2. Are you running URCL_emulator.py from elsewhere?",)

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
      line[x] = "".join(list(filter(lambda a: (a not in "," or a.isnumeric() or a.isalpha()), line[x])))
    program[y] = " ".join(line)
  return list(filter(None, program))

def convertToInstructions(program):
  global RUNRAM
  global operands
  global labelCount
  code, label = [], []
  for x in range(len(program)):
    operandList, line, operandCount, opcode = ([],program[x].split(),operands.get(program[x].split()[0], None),program[x].split()[0],)
    if line[0][0] == ".":
      label.append(line[0])
      continue
    if len(line) > 1:
      operandList = line[1:]
    cnt = 0
    flg = False
    for o in range(len(operandList)):
      opr = operandList[o]
      if opr[0] == "[":
        cnt += 1
        flg = True
        operandList[o] = operandList[o][1:]
        continue
      elif opr.count("]") > opr.count("["):
        cnt += 1
        operandList[o] = operandList[o][:-1]
        break
      elif flg:
        cnt += 1
    if cnt >= 2:
      opcode = f"{cnt}_{opcode}"
    code.append(instruction(label, opcode, operandList))
    label = []
  return list(filter(None, code))

def writeCharToConsole(char):
  global CONSOLE
  global CONSOLE_Y
  global CONSOLE_X
  if char == 10:
    CONSOLE[CONSOLE_Y].pop()
    CONSOLE.append(["█"])
    if CONSOLE_Y < 10:
      CONSOLE_Y += 1
    else:
      CONSOLE.pop(0)
    CONSOLE_X = 0
  elif char == 8:
    CONSOLE[CONSOLE_Y].pop()
    CONSOLE[CONSOLE_Y].pop()
    CONSOLE[CONSOLE_Y].append("█")
    CONSOLE_X -= 1
  elif char == 13:
    CONSOLE[CONSOLE_Y].pop()
    CONSOLE_X = 0
    CONSOLE[CONSOLE_Y][CONSOLE_X] = "█"
  else:
    CONSOLE[CONSOLE_Y][CONSOLE_X] = chr(char)
    CONSOLE_X += 1
    CONSOLE[CONSOLE_Y].append("█")
  return

def getState(program_input, databuswidth):
  global FLAG
  global REG
  global BITS
  global CONSOLE
  global CONSOLE_Y
  global CONSOLE_X
  global PC
  global PAGE
  global ADDRESS
  global FILE
  PC = 0
  cycles = 0
  BITS = databuswidth
  RAM = []
  STACK = ["-" for x in range(10)]
  REG = ["-" for x in range(128)]
  LABEL = {}
  OUTPUT = []

  PIX_DISPLAY_X = 0
  PIX_DISPLAY_Y = 0

  PIX_DISPLAY = [["  "]]

  reverseLABEL = {}
  FLAG = {
    "CF": False,
    "ZF": False,
    "NF": False,
    "OF": False
  }
  printDisplay = False
  state = ""
  maxaddr = (2**BITS)-1
  maxwidth = len(str(maxaddr))
  program = program_input
  offset = len(program) + 1
  for x,ins in enumerate(program):
    for l,lbl in enumerate(ins.label):
      if LABEL.get(lbl, None) == None:
        LABEL[lbl] = x
        reverseLABEL[x] = lbl
  for x,ins in enumerate(program):
    for y,opr in enumerate(program[x].operandList):
      word = 0
      if "[" in opr:
        opr, word = opr.split("[")
        word = int(word[:-1])
      if LABEL.get(opr, None) != None:
        program[x].operandList[y] = str(LABEL[opr])
      if opr[0] == "#":
        program[x].operandList[y] = str(int(opr[1:]) + offset)
      if opr[0] not in "$%":
        program[x].operandList[y] = str((int(program[x].operandList[y])>>BITS*word)&(2**(BITS)-1))

  for x,ins in enumerate(program):
    if ins.opcode not in ["DW"]:
      RAM.append("-")
    else:
      RAM.append(int(ins.operandList[0]))
  colorama.init()
  step = False
  show = False
  try:
    if "-step" in s.argv: step = True
    if "-show" in s.argv: show = True
  except:
    step = False
  while True:
    if REG[0] not in ["0", 0]:
      REG[0] = 0
    cycles += 1
    ins = program[PC]
    PC += 1
    operands = ins.operandList
    opcode = ins.opcode
    if opcode == "IMM":
      REG[int(operands[0][1:])] = int(operands[1])
    elif opcode == "STR":
      addr = REG[int(operands[0][1:])]
      if addr < len(RAM) or (abs(addr-len(RAM)) <= abs(addr-(maxaddr-len(STACK)))):
        while addr >= len(RAM):
          RAM.append("-")
        RAM[addr] = REG[int(operands[1][1:])]
      else:
        addr = maxaddr - addr
        while addr >= len(STACK):
          STACK.append("-")
        STACK[addr] = REG[int(operands[1][1:])]
    elif opcode == "LOD":
      addr = REG[int(operands[1][1:])]
      if addr < len(RAM) or (abs(addr-len(RAM)) <= abs(addr-(maxaddr-len(STACK)))):
        REG[int(operands[0][1:])] = int(RAM[addr])
      else:
        addr = maxaddr - addr
        while addr >= len(STACK):
          STACK.append("-")
        REG[int(operands[0][1:])] = int(STACK[addr])
    elif opcode == "JMP":
      PC = REG[int(operands[0][1:])]
    elif opcode == "BGE":
      if REG[int(operands[1][1:])] >= REG[int(operands[2][1:])]:
        PC = REG[int(operands[0][1:])]
    elif opcode == "MOV":
      REG[int(operands[0][1:])] = REG[int(operands[1][1:])]
    elif opcode == "NOT":
      REG[int(operands[0][1:])] = ~REG[int(operands[1][1:])] % 2**(BITS)
    elif opcode == "INC":
      REG[int(operands[0][1:])] = REG[int(operands[1][1:])] + 1
      updateFlags(int(operands[0][1:]))
    elif opcode == "DEC":
      REG[int(operands[0][1:])] = (REG[int(operands[1][1:])] + (2**(BITS)-1)) & 2**(BITS)-1
      updateFlags(int(operands[0][1:]))
    elif opcode == "ADD":
      REG[int(operands[0][1:])] = REG[int(operands[1][1:])] + REG[int(operands[2][1:])]
      updateFlags(int(operands[0][1:]))
    elif opcode == "SUB":
      REG[int(operands[0][1:])] = REG[int(operands[1][1:])] + (~REG[int(operands[2][1:])] % 2**(BITS))+1
      updateFlags(int(operands[0][1:]))
    elif opcode == "RSH":
      REG[int(operands[0][1:])] = REG[int(operands[1][1:])] // 2
      updateFlags(int(operands[0][1:]))
    elif opcode == "LSH":
      REG[int(operands[0][1:])] = REG[int(operands[1][1:])] * 2
      updateFlags(int(operands[0][1:]))
    elif opcode == "XOR":
      REG[int(operands[0][1:])] = REG[int(operands[1][1:])] ^ REG[int(operands[2][1:])]
      updateFlags(int(operands[0][1:]))
    elif opcode == "AND":
      REG[int(operands[0][1:])] = REG[int(operands[1][1:])] & REG[int(operands[2][1:])]
      updateFlags(int(operands[0][1:]))
    elif opcode == "OR":
      REG[int(operands[0][1:])] = REG[int(operands[1][1:])] | REG[int(operands[2][1:])]
      updateFlags(int(operands[0][1:]))
    elif opcode == "NOR":
      REG[int(operands[0][1:])] = ~(REG[int(operands[1][1:])] | REG[int(operands[2][1:])]) % 2**(BITS)
      updateFlags(int(operands[0][1:]))
    elif opcode == "NAND":
      REG[int(operands[0][1:])] = ~(REG[int(operands[1][1:])] & REG[int(operands[2][1:])]) % 2**(BITS)
      updateFlags(int(operands[0][1:]))
    elif opcode == "XNOR":
      REG[int(operands[0][1:])] = ~(REG[int(operands[1][1:])] | REG[int(operands[2][1:])]) % 2**(BITS)
      updateFlags(int(operands[0][1:]))
    elif opcode == "IN":
      try:
        if operands[1] == "%RNG":
          REG[int(operands[0][1:])] = randint(0, (2**BITS)-1)
        elif operands[1] == "%BUS":
          if not FILE:
            if not os.path.isfile(f"Emulator/Storage/{BITS}_{PAGE}.bin"):
              with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "w+b") as f:
                f.write(bytearray(splitIntoBytes(0)))
                f.close()
            words = BITS//8
            if not words:
              words = 1
            with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "rb") as f:
              while True:
                fullword = f.read(words)
                if fullword:
                  newfullword = 0
                  for w,word in enumerate(fullword):
                    newfullword += int(word)<<(8*(words-w-1))
                  FILE.append(newfullword)
                else:
                  break
              f.close()
          try:
            REG[int(operands[0][1:])] = FILE[ADDRESS]
          except:
            REG[int(operands[0][1:])] = 0
        elif operands[1] == "%TEXT":
          special = {
            r"\n": 10,
            r"\LF": 10,
            r"\BS": 8,
            r"\CR": 13,
            r"\SP": 32,
          }
          char = input(f"IN (char): ")
          if special.get(char):
            char = special[char]
          else:
            char = ord(char)
          REG[int(operands[0][1:])] = char
          printDisplay = True
        elif operands[1] in ("%ASCII","%CHAR5","%CHAR6","%ASCII7","%UTF8"):
          REG[int(operands[0][1:])] = ord(input(f"IN (char): "))
        elif operands[1] == "%BIN":
          REG[int(operands[0][1:])] = int(input(f"IN (bin ): "), 2)
        elif operands[1] == "%HEX":
          REG[int(operands[0][1:])] = int(input(f"IN (hex ): "), 16)
        else:
          REG[int(operands[0][1:])] = int(input(f"IN (num ): "))
      except:
        REG[int(operands[0][1:])] = 0
      REG[int(operands[0][1:])] = REG[int(operands[0][1:])] & ((2**BITS)-1)
    elif opcode == "OUT":
      printDisplay = True
      val = REG[int(operands[1][1:])]
      if operands[0] == "%NUMB":
        OUTPUT.append(val)
      elif operands[0] == "%ADDR":
        ADDRESS = val
      elif operands[0] == "%PAGE":
        oldPage = PAGE
        PAGE = val
        if oldPage != PAGE:
          if not FILE:
            words = BITS//8
            if not words:
              words = 1
            if not os.path.isfile(f"Emulator/Storage/{BITS}_{PAGE}.bin"):
              with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "w+b") as f:
                f.write(bytearray(splitIntoBytes(0)))
                f.close()
            with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "rb") as f:
              while True:
                fullword = f.read(words)
                if fullword:
                  newfullword = 0
                  for w,word in enumerate(fullword):
                    newfullword += int(word)<<(8*(words-w-1))
                  FILE.append(newfullword)
                  FILE.append(f.read(2))
                else:
                  break
              f.close()
      elif operands[0] == "%BUS":
        if not FILE:
          words = BITS//8
          if not words:
            words = 1
          if not os.path.isfile(f"Emulator/Storage/{BITS}_{PAGE}.bin"):
            with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "w+b") as f:
              f.write(bytearray(splitIntoBytes(0)))
              f.close()
          with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "rb") as f:
            while True:
              fullword = f.read(words)
              if fullword:
                newfullword = 0
                for w,word in enumerate(fullword):
                  newfullword += int(word)<<(8*(words-w-1))
                FILE.append(newfullword)
                FILE.append(f.read(2))
              else:
                break
            f.close()
        while ADDRESS >= len(FILE):
          FILE.append(0)
        FILE[ADDRESS] = val
        with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "w+b") as f:
          fileAsBytes = []
          for num in FILE:
            fileAsBytes += splitIntoBytes(num)
          f.write(bytearray(fileAsBytes))
          f.close()
      elif operands[0] == "%TEXT":
        writeCharToConsole(val)
      elif operands[0] == "%BIN":
        OUTPUT.append(bin(val))
      elif operands[0] == "%HEX":
        OUTPUT.append(hex(val))
      elif operands[0] == "%X":
        PIX_DISPLAY_X = val
      elif operands[0] == "%Y":
        PIX_DISPLAY_Y = val
      elif operands[0] in ("%ASCII","%CHAR5","%CHAR6","%ASCII7","%UTF8"):
        OUTPUT.append(val)
      elif operands[0] == "%COLOR" or operands[0] == "%COLOUR":
        draw = "  "
        if val != 0:
          draw = "██"
        while len(PIX_DISPLAY) <= PIX_DISPLAY_Y:
          PIX_DISPLAY.append(["  "])
        while len(PIX_DISPLAY[PIX_DISPLAY_Y]) <= PIX_DISPLAY_X:
          PIX_DISPLAY[PIX_DISPLAY_Y].append("  ")
        PIX_DISPLAY[PIX_DISPLAY_Y][PIX_DISPLAY_X] = draw
      else:
        OUTPUT.append(val)
    elif opcode == "BRZ":
      if REG[int(operands[1][1:])] == 0:
        PC = REG[int(operands[0][1:])]
    elif opcode == "BNZ":
      if REG[int(operands[1][1:])] != 0:
        PC = REG[int(operands[0][1:])]
    elif opcode == "HLT":
      break
    elif opcode == "NOP":
      pass
    elif opcode[0].isnumeric() and "_" in opcode:
      w, opcode = opcode.split("_")
      w = int(w)
      if opcode == "BGE":
        if REG[int(operands[-2][1:])] >= REG[int(operands[-1][1:])]:
          PC = sum(REG[int(operands[x][1:])]<<BITS*(w-x-1) for x in range(w))
      elif opcode == "LOD":
        REG[int(operands[0][1:])] = int(RAM[sum(REG[int(operands[x+1][1:])]<<BITS*(w-x-1) for x in range(w))])
      elif opcode == "STR":
        val = sum(REG[int(operands[x][1:])]<<BITS*(w-x-1) for x in range(w))
        while len(RAM) <= val:
          RAM.append("-")
        RAM[val] = REG[int(operands[-1][1:])]
      elif opcode == "OUT":
        val = sum(REG[int(operands[x+1][1:])]<<BITS*(w-x-1) for x in range(w))
        printDisplay = True
        if operands[0] == "%NUMB":
          OUTPUT.append(val)
        elif operands[0] == "%ADDR":
          ADDRESS = val
        elif operands[0] == "%PAGE":
          oldPage = PAGE
          PAGE = val
          if oldPage != PAGE:
            if not FILE:
              words = BITS//8
              if not words:
                words = 1
              if not os.path.isfile(f"Emulator/Storage/{BITS}_{PAGE}.bin"):
                with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "w+b") as f:
                  f.write(bytearray(splitIntoBytes(0)))
                  f.close()
              with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "rb") as f:
                while True:
                  fullword = f.read(words)
                  if fullword:
                    newfullword = 0
                    for z,word in enumerate(fullword):
                      newfullword += int(word)<<(8*(words-z-1))
                    FILE.append(newfullword)
                    FILE.append(f.read(2))
                  else:
                    break
                f.close()
        elif operands[0] == "%BUS":
          if not FILE:
            words = BITS//8
            if not words:
              words = 1
            if not os.path.isfile(f"Emulator/Storage/{BITS}_{PAGE}.bin"):
              with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "w+b") as f:
                f.write(bytearray(splitIntoBytes(0)))
                f.close()
            with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "rb") as f:
              while True:
                fullword = f.read(words)
                if fullword:
                  newfullword = 0
                  for z,word in enumerate(fullword):
                    newfullword += int(word)<<(8*(words-z-1))
                  FILE.append(newfullword)
                  FILE.append(f.read(2))
                else:
                  break
              f.close()
          while ADDRESS >= len(FILE):
            FILE.append(0)
          FILE[ADDRESS] = val
          with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "w+b") as f:
            fileAsBytes = []
            for num in FILE:
              fileAsBytes += splitIntoBytes(num)
            f.write(bytearray(fileAsBytes))
            f.close()
        elif operands[0] == "%TEXT":
          writeCharToConsole(val)
        elif operands[0] == "%BIN":
          OUTPUT.append(bin(val))
        elif operands[0] == "%HEX":
          OUTPUT.append(hex(val))
        elif operands[0] == "%X":
          PIX_DISPLAY_X = val
        elif operands[0] == "%Y":
          PIX_DISPLAY_Y = val
        elif operands[0] in ("%ASCII","%CHAR5","%CHAR6","%ASCII7","%UTF8"):
          OUTPUT.append(val)
        elif operands[0] == "%COLOR" or operands[0] == "%COLOUR":
          draw = "  "
          if val != 0:
            draw = "██"
          while len(PIX_DISPLAY) <= PIX_DISPLAY_Y:
            PIX_DISPLAY.append(["  "])
          while len(PIX_DISPLAY[PIX_DISPLAY_Y]) <= PIX_DISPLAY_X:
            PIX_DISPLAY[PIX_DISPLAY_Y].append("  ")
          PIX_DISPLAY[PIX_DISPLAY_Y][PIX_DISPLAY_X] = draw
        else:
          OUTPUT.append(val)
      elif opcode == "IN":
        inval = 0
        try:
          if operands[-1] == "%RNG":
            inval = randint(0, (2**BITS)-1)
          elif operands[-1] == "%BUS":
            if not FILE:
              if not os.path.isfile(f"Emulator/Storage/{BITS}_{PAGE}.bin"):
                with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "w+b") as f:
                  f.write(bytearray(splitIntoBytes(0)))
                  f.close()
              words = BITS//8
              if not words:
                words = 1
              with open(f"Emulator/Storage/{BITS}_{PAGE}.bin", "rb") as f:
                while True:
                  fullword = f.read(words)
                  if fullword:
                    newfullword = 0
                    for z,word in enumerate(fullword):
                      newfullword += int(word)<<(8*(words-z-1))
                    FILE.append(newfullword)
                  else:
                    break
                f.close()
            try:
              inval = FILE[ADDRESS]
            except:
              inval = 0
          elif operands[-1] == "%TEXT":
            special = {
              r"\n": 10,
              r"\LF": 10,
              r"\BS": 8,
              r"\CR": 13,
              r"\SP": 32,
            }
            char = input(f"IN (char): ")
            if special.get(char):
              char = special[char]
            else:
              char = ord(char)
            inval = char
            printDisplay = True
          elif operands[-1] in ("%ASCII","%CHAR5","%CHAR6","%ASCII7","%UTF8"):
            inval = ord(input(f"IN (char): "))
          elif operands[-1] == "%BIN":
            inval = int(input(f"IN (bin ): "), 2)
          elif operands[-1] == "%HEX":
            inval = int(input(f"IN (hex ): "), 16)
          else:
            inval = int(input(f"IN (num ): "))
        except:
          inval = 0
        regs = operands[:-1].copy()
        for r, register in enumerate(regs):
          REG[int(register[1:])] = (inval>>(len(regs)-r-1)*BITS)&((2**BITS)-1)
    if not printDisplay and not step and not (show and cycles % 1000 == 0):
      continue
    printDisplay = False
    columns = [[],[],[],[],[]]
    columns[0].append("\033[1;1H- Memory")
    flg0 = False
    mcnt = 0
    for x,val in enumerate(RAM):
      lbl = reverseLABEL.get(x, "")
      if val != "-":
        flg0 = True
        mcnt += 1
        columns[0].append(f"├ {x:>{maxwidth}}: {val} ({lbl})" if lbl else f"├ {x:>{maxwidth}}: {val}")
      if mcnt > 17:
        remaining = RAM[x+1:].count("-")
        columns[0].append(f"├ (approx. {len(RAM)-x-remaining} more values)")
        mcnt += len(RAM)-x-remaining
        break
    if flg0:
      columns[0].append(f"├ {'...':>{maxwidth}}")
    STACK.reverse()
    flg1 = False
    scnt = 0
    for x,val in enumerate(STACK):
      addr2 = maxaddr - len(STACK) + x + 1
      if val != "-":
        flg1 = True
        scnt += 1
        columns[0].append(f"├ {addr2:>{maxwidth}}: {val}")
      if scnt > 17:
        columns[0].append(f"├ (approx. {len(STACK)-x} more values)")
        scnt += len(STACK)-x
        break
    if not flg1:
      columns[0].append(f"├ {'(all empty)':>{maxwidth}}")
    STACK.reverse()
    columns[1].append("      - Registers")
    flg2 = False
    rcnt = 0
    maxwidth = len(str(BITS))
    for x,val in enumerate(REG):
      if val != "-":
        flg2 = True
        rcnt += 1
        columns[1].append(f"├ {x:>{maxwidth}}: {val}")
    if not flg2:
      columns[1].append(f"├ {'(all empty)':>{maxwidth}}")
    columns[2].append(f"      - Headers")
    columns[2].append(f"├ MINREG: {rcnt}")
    columns[2].append(f"├ MINRAM: {mcnt}")
    columns[2].append(f"├ MINSTK: {scnt}")
    columns[2].append("")
    columns[2].append(f"- Executing")
    columns[2].append(f"├ {PC}: {opcode} {', '.join(operands)}")
    columns[2].append(f"")
    columns[2].append(f"- Console")
    for line in CONSOLE:
      columns[2].append(f"├ {''.join(line)}")
    columns[3].append(f"      - Runtime: {cycles} clock cycles")
    columns[3].append("")
    columns[3].append(f"Display X: {PIX_DISPLAY_X}")
    columns[3].append(f"Display Y: {PIX_DISPLAY_Y}")
    columns[3].append("")
    for row in PIX_DISPLAY:
      columns[3].append("".join(row))
    columns[1].append("")
    columns[1].append(f"- Output")
    offset = 0
    if len(OUTPUT) > 10:
      offset = len(OUTPUT)-10
    for x in range(offset, len(OUTPUT)):
      columns[1].append(f"├ {OUTPUT[x]}")
    highest = max([len(z) for z in columns])
    for x in range(highest):
      output = ""
      for y in range(len(columns)):
        try: output += f"{columns[y][x]:<30}"
        except: output += f"{' ':<30}"
      print(output)
    if step:
      input()
  return state

def main():
  global operands
  global RUNRAM
  global databuswidth
  try:
    databuswidth = int(s.argv[1])
  except:
    print("Memory: BITS**2 addresses")
    print("Registers: BITS registers")
    databuswidth = int(input("Enter BITS: "))
  try:
    progName = s.argv[2]
  except:
    progName = input("Program name (with extension): ")
  hide_cursor()
  program = importProgram(progName)
  program = removeComments(program)
  program = convertToInstructions(program)
  #print('\x1b[2J')
  #state = getState(program, databuswidth)
  try:
    print('\x1b[2J')
    state = getState(program, databuswidth)
  except Exception as ex:
    if ex.__class__ is KeyboardInterrupt:
      print("------------ Program exited. ---------------------------------------")
    else:
      print("------------ The emulator has crashed! :( --------------------------")
      print(f"URCL instruction number: {PC} (this does not count labels)")
      print("--------------------------------------------------------------------")
      print(traceback.format_exc())
      print("------------ Potential causes (in order of probability) ------------")
      if ex.__class__ is IndexError:
        print(f"├ [███──] Your program does not have a HLT.")
        print(f"├ [█────] Your program uses too much RAM for this bit width. (Max is {(2**BITS)-1})")
        print(f"├ [█────] Your program uses too many registers. (Max is 32)")
      elif ex.__class__ is ValueError:
        print(f"├ [███──] You're LOD-ing from a memory address that hasn't been written to yet.")
        print(f"├ [██───] You're operating on a register that hasn't been initialised with IMM yet.")
      print("--------------------------------------------------------------------")
if __name__ == "__main__":
  main()