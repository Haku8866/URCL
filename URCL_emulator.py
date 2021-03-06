import sys as s
import os
import colorama
import time
import traceback
from random import randint

operands = {"NEG": 2,"DW": 1,"DD": 1,"DQ": 1,"ADD": 3,"SUB": 3,"BSR": 3,"BSL": 3,"ADC": 3,"SBB": 3,"INC": 2,"DEC": 2,"MOV": 2,"IMM": 2,"XOR": 3,"AND": 3,"OR": 3,"NOR": 3,"NAND": 3,"XNOR": 3,"NOT": 2,"LOD": 2,"STR": 2,"JMP": 1,"BRC": 1,"BNC": 1,"BRZ": 1,"BNZ": 1,"BRN": 1,"BRP": 1,"BZR": 2,"BZN": 2,"NOP": 0,"HLT": 0,"MLT": 3,"DIV": 3,"MOD": 3,"SQRT": 2,"CAL": 1,"RET": 0,"PSH": 1,"POP": 1,"BRL": 3,"BRG": 3,"BRE": 3,"BNE": 3,"IN": 2,"OUT": 2,"BOD": 2,"BEV": 2,"RSH": 2,"LSH": 2,"CMP": 2,"SRS": 3,"BSS": 3,"BLE": 3,"BGE": 3,"BITS": 2,"MINREG": 1,"RUN": 1,"MINRAM": 1,"IMPORT": 0,"NAME": 1,"OPS": 1,"REG": 1,"IN": 1,"SETE": 3,"SETNE": 3,"SETG": 3,"SETL": 3,"SETGE": 3,"SETLE": 3,}
RUNRAM = True
databuswidth = 8
PC = 0

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
      line[x] = "".join(list(filter(lambda a: (a in " _.-+=*<()>$#%" or a.isnumeric() or a.isalpha()), line[x])))
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
    elif operandCount != None:
      operandList = line[1:]
      code.append(instruction(label, opcode, operandList))
      label = []
    else:
      end(f"Unknown instruction '{line[0]}'","- try checking:\n1. Is the file written in the lastest version of URCL?\n2. If so, has anyone raised this missing feature on the URCL discord yet? (https://discord.gg/jWRr2vx)",)
  return list(filter(None, code))

def getState(program_input, databuswidth):
  global FLAG
  global REG
  global BITS
  global PC
  PC = 0
  cycles = 0
  BITS = databuswidth
  RAM = []
  STACK = ["-" for x in range(10)]
  REG = ["-" for x in range(BITS)]
  LABEL = {}
  OUTPUT = []

  PIX_DISPLAY_X = 0
  PIX_DISPLAY_Y = 0

  PIX_DISPLAY = [["  " for x in range(0, 16)] for y in range(0, 16)]

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
    if ins.opcode not in ["DW"]:
      RAM.append("-")
    else:
      RAM.append(ins.operandList[0])
    for y,operand in enumerate(ins.operandList):
      if operand[0] == "#":
        program[x].operandList[y] = str(int(operand[1:]) + offset)
  colorama.init()
  step = False
  try:
    if "-step" in s.argv: step = True
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
      if operands[1][0] == ".":
        REG[int(operands[0][1:])] = LABEL[operands[1]]
      else:
        REG[int(operands[0][1:])] = int(operands[1])
    elif opcode == "STR":
      if operands[0][0] == "$":
        addr = REG[int(operands[0][1:])]
      elif operands[0][0] == ".":
        addr = LABEL.get(operands[0])
      else:
        addr = int(operands[0])
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
      if operands[1][0] == "$":
        addr = REG[int(operands[1][1:])]
      elif operands[1][0] == ".":
        addr = LABEL.get(operands[1])
      else:
        addr = int(operands[1])
      if addr < len(RAM) or (abs(addr-len(RAM)) <= abs(addr-(maxaddr-len(STACK)))):
        while addr >= len(RAM):
          RAM.append("-")
        REG[int(operands[0][1:])] = int(RAM[addr])
      else:
        addr = maxaddr - addr
        while addr >= len(STACK):
          STACK.append("-")
        REG[int(operands[0][1:])] = STACK[addr]
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
      REG[int(operands[0][1:])] = REG[int(operands[1][1:])] + (~1 % 2**(BITS))+1
      updateFlags(int(operands[0][1:]))
    elif opcode == "ADD":
      REG[int(operands[0][1:])] = REG[int(operands[1][1:])] + REG[int(operands[2][1:])]
      updateFlags(int(operands[0][1:]))
    elif opcode == "SUB":
      REG[int(operands[0][1:])] = REG[int(operands[1][1:])] + (~REG[int(operands[2][1:])] % 2**(BITS))+1
      updateFlags(int(operands[0][1:]))
    elif opcode == "JMP":
      if operands[0][0] == "$":
        PC = REG[int(operands[0][1:])]
      else:
        PC = LABEL[operands[0]]
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
        else:
          REG[int(operands[0][1:])] = int(input(f"IN (num between 0 and {2**BITS-1}): "))
      except:
        REG[int(operands[0][1:])] = 0
    elif opcode == "OUT":
      printDisplay = True
      if operands[0] == "%NUMB":
        OUTPUT.append(REG[int(operands[1][1:])])
      elif operands[0] == "%TEXT":
        OUTPUT.append(chr(REG[int(operands[1][1:])]))
      elif operands[0] == "%X":
        PIX_DISPLAY_X = REG[int(operands[1][1:])]
      elif operands[0] == "%Y":
        PIX_DISPLAY_Y = REG[int(operands[1][1:])]
      elif operands[0] == "%COLOR" or operands[0] == "%COLOUR":
        draw = "  "
        if REG[int(operands[1][1:])] != 0:
          draw = "██"
        PIX_DISPLAY[PIX_DISPLAY_Y][PIX_DISPLAY_X] = draw
      else:
        OUTPUT.append(REG[int(operands[1][1:])])
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
    if not printDisplay and not step:
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
        columns[0].append(f"├ (approx. {len(RAM)-x} more values)")
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
  try:
    print('\x1b[2J')
    state = getState(program, databuswidth)
  except Exception as ex:
    #if ex.__class__ is TypeError:
    #  print(f"Null reference exception! You're either:\n - 1) Using a register that hasn't been loaded with an IMM <reg> <val> instruction.\n - 2) Loading a value from memory that hasn't been set with a STR <addr> <val/reg> instruction.\nVariables need to be set before being used, as the CPU won't set everything to 0 before running your program.")
    #elif ex.__class__ is IndexError:
    #  print(f"Index out of bounds error! You're either:\n - 1) Using too many registers (this CPU only has {databuswidth}), try using some memory instead.\n - 2) Using too much memory (this CPU only has {2**BITS} words), try making your program more efficient, or target {databuswidth*2} bit CPUs instead.")
    #else:
      print(f"URCL code line: {PC}")
      print(traceback.format_exc())
if __name__ == "__main__":
  main()