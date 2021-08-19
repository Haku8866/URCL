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
      elif (opr[0] == "+" or opr[0] == "-") and ins.opcode.type == "branch":
        ins.operandList[y] = operand("relativeAddr", int(opr), word)
      elif opr == "SP":
        ins.operandList[y] = operand("stackPtr", "", word)
      elif opr[0] == "&":
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
from random import randint
import sys, traceback, colorama, time
from colorama import Fore,Back,Style
colorama.init(autoreset=True)
class grid():
  def __init__(self, columns, rows, width):
    self.grid = [["" for x in range(rows)] for y in range(columns)]
    self.width = width
  def show(self):
    print("\033[1;1H")
    highest = max([len(z) for z in self.grid])
    for x in range(highest):
      out = ""
      for col in self.grid:
        if len(col)-1 >= x:out+=f"{col[x]:{self.width}}"
        else:out+=f"{' ':{self.width}}"
      print(out)
def stringIns(ins):
  prefixes = {"register":"$","memAddr":"#","label":"."}
  return ins.opcode.name + " " + ", ".join([prefixes.get(opr.type, "") + str(opr.value) if opr.word == 0 else prefixes.get(opr.type, "") + str(opr.value) + f"[{opr.word}]" for opr in ins.operandList])
def main(program,bits,step,show,slow):
  for x,ins in enumerate(program):
    for o,opr in enumerate(ins.operandList):
      if opr.type in ("number","memAddr"):
        program[x].operandList[o].value = (opr.value>>bits*opr.word)&((2**(bits))-1)
        program[x].operandList[o].word = 0
    for l,lbl in enumerate(ins.label):
      for y,ins2 in enumerate(program):
        for o,opr in enumerate(ins2.operandList):
          if opr.type=="label" and opr.value == lbl.value:
            program[y].operandList[o]=operand("number",(x>>bits*opr.word)&((2**(bits))-1))
  display = grid(4,1,30)
  pc,memory,registers,out,cycles=0,{},{},[],0
  getreg = lambda a,b:registers[b.operandList[a].value]
  try:
    while True:
      registers[0]=0
      ins,pc,cycles=program[pc],pc+1,cycles+1
      if ins.opcode.name=="ADD":registers[ins.operandList[0].value]=(getreg(1,ins)+getreg(2,ins))&((2**(bits))-1)
      elif ins.opcode.name=="IMM":registers[ins.operandList[0].value]=ins.operandList[1].value&((2**(bits))-1)
      elif ins.opcode.name=="NOR":registers[ins.operandList[0].value]=~(getreg(1,ins)|getreg(2,ins))&((2**(bits))-1)
      elif ins.opcode.name=="STR":memory[registers[ins.operandList[0].value]]=getreg(1,ins)
      elif ins.opcode.name=="LOD":registers[ins.operandList[0].value]=memory[getreg(1,ins)]
      elif ins.opcode.name=="RSH":registers[ins.operandList[0].value]=getreg(1,ins)//2
      elif ins.opcode.name=="BGE" and getreg(1,ins)>=getreg(2,ins):pc=getreg(0,ins)
      elif ins.opcode.name=="IN" and ins.operandList[1].value=="%RNG":registers[ins.operandList[0].value]=randint(0,(2**(bits))-1)
      elif ins.opcode.name=="OUT":out.append(getreg(1,ins))
      elif "BGE" in ins.opcode.name:
        if ins.operandList[-1].type == "register":op1 = getreg(-1, ins)
        else:op1 = ins.operandList[-1].value
        if ins.operandList[-2].type == "register":op2 = getreg(-2, ins)
        else:op2 = ins.operandList[-2].value
        if op2 < op1:continue
        w = int(ins.opcode.name.split("_")[0])
        if ins.operandList[0].type == "register":pc=sum(getreg(x,ins)<<bits*(w-x-1) for x in range(w))
        else:pc=sum(ins.operandList[x].value<<bits*(w-x-1) for x in range(w))
      elif "LOD" in ins.opcode.name:
        w = int(ins.opcode.name.split("_")[0])
        registers[ins.operandList[0].value]=memory[sum(getreg(x+1,ins)<<bits*(w-x-1) for x in range(w))]
      elif "STR" in ins.opcode.name:
        w = int(ins.opcode.name.split("_")[0])
        memory[sum(getreg(x,ins)<<bits*(w-x-1) for x in range(w))]=getreg(-1,ins)
      elif "OUT" in ins.opcode.name:
        w = int(ins.opcode.name.split("_")[0])
        out.append(sum(getreg(x+1,ins)<<bits*(w-x-1) for x in range(w)))
      if step or show or slow or ins.opcode.name=="OUT" or "OUT" in ins.opcode.name or cycles%10000==0:
        display.grid[0]=[f"#{m}: {memory[m]}" for m in memory]
        display.grid[1]=[f"${r[0]}: {r[1]}" for r in sorted(registers.items())]
        display.grid[2]=[f"{o}: {out[o]}" for o in range(len(out))]
        display.grid[3]=[f"{Fore.YELLOW}>>> {i:>{len(str(len(program)))}}: {stringIns(program[i])}{' '*20}" if i==pc else f"    {i:>{len(str(len(program)))}}: {stringIns(program[i])}{' '*20}" if i>=0 and i<len(program) else f"    {i:>{len(str(len(program)))}}: -------{' '*20}" for i in range(pc-10, pc+10)]
        for c,col in enumerate(display.grid):
          if len(col)>30:display.grid[c]=col[-30:]
        header = ("MEMORY:","REGISTERS:","OUTPUT:","CODE:")
        for h,head in enumerate(header):
          display.grid[h][0:0]=[head]
        display.grid[3]+=[f"CYCLES: {cycles}"]
        display.show()
        if step:input()
        elif slow:time.sleep(1)
  except:
    print(f"URCL code line: {pc}")
    input(traceback.format_exc())
if __name__ == "__main__":
  step,show,slow=False,False,False
  if len(sys.argv) > 1:
    try:bits=int(sys.argv[1])
    except:print(r"Format: py URCL_core_emu.py {bits} {program.urcl} {step/show}")
  else:bits=int(input("BITS: "))
  if len(sys.argv) > 2:
    try:program=importProgram(sys.argv[2])
    except:print(r"Format: py URCL_core_emu.py {bits} {program.urcl} {step/show}")
  else:program=importProgram(input("PROGRAM NAME: "))
  if len(sys.argv) > 3:
    if "step" in sys.argv[3]:step=True
    elif "show" in sys.argv[3]:show=True
    elif "slow" in sys.argv[3]:slow=True
    else:print(r"Format: py URCL_core_emu.py {bits} {program.urcl} {step/show/slow}")
  program=parseURCL(program)
  main(program,bits,step,show,slow)