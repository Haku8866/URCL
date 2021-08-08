import URCL
from URCL import parseURCL,importProgram,printIns,operand
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
  prefixes = {"register":"$","memAddr":"#","label":".",}
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