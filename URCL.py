import json
import sys
ISA_input = input("Compile to which ISA? ")
try:
    exec(f"import {ISA_input} as ISA")
except:
    print("File not found or file is invalid. (Is it in a different folder?)")
    input()
    sys.exit()

INS_Table = ISA.Instruction_table
CPU_Stats = ISA.CPU_stats

count = 0
code = []
var = []
label_list = []
labels = {}

branching_ops = ["BRP","BRN","BNZ","BRZ","BNC","BRC","BRA","BRL","BRG","BRE","BNE","BEV","BOD","BGE","BLE"]
operands = {"ADD":   3,"SUB":   3,"BSR":   3,"BSL":   3,"ADC":   3,"SBB":   3,"INC":   2,
            "DEC":   2,"MOV":   2,"IMM":   2,"XOR":   3,"AND":   3,"OR":    3,"NOR":   3,
            "NAND":  3,"XNOR":  3,"NOT":   2,"LOAD":  2,"STORE": 2,"BRA":   1,"BRC":   1,
            "BNC":   1,"BRZ":   1,"BNZ":   1,"BRN":   1,"BRP":   1,"NOP":   0,"HLT":   0,
            "MLT":   3,"DIV":   3,"MOD":   3,"SQRT":  2,"CAL":   1,"RET":   0,"PSH":   1,
            "POP":   1,"BRL":   3,"BRG":   3,"BRE":   3,"BNE":   3,"IN":    2,"OUT":   2,
            "BOD":   2,"BEV":   2,"RSH":   2,"LSH":   2,"CMP":   2,"SRS":   3,"BSS":   3,
            "BLE":   3,"BGE":   3,"BITS":  2,"MINREG":1,"MINRAM":1,"IMPORT":0,"SETE":  3,
            "SETNE": 3,"SETG":  3,"SETL":  3,"SETGE": 3,"SETLE": 3}

cmplx_subs = {
    "MLT": ["MOV *1 <B>","MOV *2 <C>","IMM <A> 0","BEV +2 *2","ADD <A> <A> *1","LSH *1 *1","RSH *2 *2","BNZ -4"], # Original by: Kuggo              Optimised by: Haku
    "DIV": ["MOV <A> <B>","MOV *1 <C>","IMM *2 0","IMM *3 1","LSH *2 *2","LSH <A> <A>","BRC +8","CMP *2 *1","BRN +3","SUB *2 *2 *1","INC <A> <A>","LSH *3 *3","BRC +4","BRA -9","INC *2 *2","BRA -8"], # Original by: Kuggo
    "MOD": [],
    "CAL": [],
    "RET": [],
    "PSH": [],
    "POP": [],
    "BRL": ["SUB $0 <B> <C>","BNC <A>"],                                                                          # Original by: Mod Punchtree
    "BRG": ["SUB $0 <C> <B>","BNC <A>"],                                                                          # Original by: Mod Punchtree
    "BRE": ["CMP <B> <C>","BRZ <A>"],                                                                             # Original by: Verlio_H
    "BNE": ["CMP <B> <C>","BNZ <A>"],                                                                             # Original by: Verlio_H
    "BOD": [],
    "BEV": [],
    "BLE": [],
    "BGE": [],
    "IN":  ["NOP"],
    "OUT": ["NOP"],
    "BSR": ["MOV *1 <C>","MOV <A> <B>","RSH <A> <A>","DEC *1 *1","BNZ -2"],                                       # Original by: Verlio_H           Optimised by: Haku
    "BSL": ["MOV *1 <C>","MOV <A> <B>","LSH <A> <A>","DEC *1 *1","BNZ -2"],                                       # Original by: Verlio_H           Optimised by: Haku
    "SRS": [],
    "BSS": [],
    "CMP": ["SUB $0 <A> <B>"],                                                                                    # Original by: Verlio_H
    "ADC": ["BNC +3","ADD <A> <B> <C>","BRA +3","ADD <A> <B> <C>","INC <A> <A>"],                                 # Original by: Haku               Optimised by: Mod Punchtree
    "SBB": ["BNC +3","SUB <A> <B> <C>","BRA +3","SUB <A> <B> <C>","DEC <A> <A>"],                                 # Original by: Mod Punchtree
    "SETE":  [],
    "SETNE": [],
    "SETG":  [],
    "SETL":  [],
    "SETGE": [],
    "SETLE": [],
    }

fname = input("File to compile? ")
try:
    f = open(fname, "r", encoding="utf8")
    file = []
    for line in f:
        file.append(line)
    f.close()
except:
    print(f"'{fname}' does not exist. (Is it in a different folder?)")
    input()
    sys.exit()

def snip(line):
    line = line.rstrip("\n")
    line = line.split("//")[0]
    line = line.split(";")[0]
    line = line.strip()
    line = line.split(" ")
    for x in range(0, len(line)):
        line[x] = line[x].strip()
        striplist = []
        for char in line[x]:
            if char.isalpha() or char.isnumeric():
                continue
            elif char not in " .-+=*#$()":
                striplist.append(char)
        if striplist != []:
            for char in striplist:
                line[x] = line[x].replace(char,"")
    line = " ".join(line)
    return line

def fixLabels(file):
    global count
    for x in range(0, len(file)):
        line = file[x].split(" ")
        try:
            ops = operands[line[0]]
        except:
            if line == "":
                continue
            if line[0][0] == ".":
                label = line[0]
                file[x+1] += f" ({label})"
                file[x] = ""
            else:
                file[x] = ""
        if line[0] in branching_ops:
            if line[1][0] == ".":
                label = line[1][1:]
            else:
                label = line[1]
            if label[0] == "+":
                file[x+int(label[1:])] += f" (__LABEL__#{count})"
            elif label[0] == "-":
                file[x-int(label[1:])] += f" (__LABEL__#{count})"
            else:
                continue
            file[x] = file[x].replace(label.strip(), f"__LABEL__#{count}")
            label = f"__LABEL__#{count}"
            label_list.append(label)
            count += 1

def countRegs(file):
    global var
    for y in range(0, len(file)):
        line = file[y]
        line = line.split()
        ops = operands[line[0]]
        if ops != 0:
            for x in range(1, ops+1):
                try:
                    line[x] = str(int(line[x], base=0))
                except:
                    if line[x][0] == "#":
                        num = 0
                        try:
                            if line[x][1] == "+":
                                num = int(line[x][2:])
                            elif line[x][1] == "-":
                                num = int(line[x][2:])*-1
                        except:
                            pass
                        line[x] = str(int(CPU_Stats["DATABUS_WIDTH"])+num)
                    elif line[x][0] == "R":
                        line[x] = "$" + line[x][1:]
                    if not line[x] in var and line[x] != "$0" and line[x][0] != ".":
                        try:
                            int(line[x])
                        except:
                            var.append(line[x])
        file[y] = " ".join(line)
    return file

def replaceComplex(file):
    global var
    global repeat
    global tvar
    tvar2 = []
    br = False
    for x in range(0, len(file)):
        line = file[x].split()
        if line[0] == "BITS" or line[0] == "IMPORT" or line[0] == "MINREG" or line[0] == "MINRAM":
            continue
        if INS_Table[line[0]] == []:
            if cmplx_subs[line[0]] != []:
                repeat = True
                br = True
                newlines = cmplx_subs[line[0]].copy()
                ops = operands[line[0]]
                try:
                    label = " " + line[ops+1]
                except:
                    label = ""
                for y in range(0, len(newlines)):
                    newlines[y] = newlines[y].strip()
                    if ops > 0:
                        newlines[y] = newlines[y].replace("<A>", line[1])
                    if ops > 1:
                        newlines[y] = newlines[y].replace("<B>", line[2])
                    if ops > 2:
                        newlines[y] = newlines[y].replace("<C>", line[3])
                    if y == 0 and label != "":
                        newlines[y] += label
                    newline = newlines[y].split(" ")
                    ops2 = operands[newline[0]]
                    if ops2 > 0:
                        for z in range(1, ops2+1):
                            if newline[z][0] == "*":
                                var = list(filter(None, var))
                                tvar2.append("$" + str(int(newline[z][1:])+len(var)))
                                newline[z] = "$" + str(int(newline[z][1:])+len(var))
                    newlines[y] = " ".join(newline)
                newlines.reverse()
                file.pop(x)
                for newline in newlines:
                    file.insert(x, newline)
        if len(tvar2) > len(tvar):
            tvar = tvar2
        if br:
            break
omitted = 0
file = list(filter(None, file))
for x in range(0, len(file)): 
    file[x] = snip(file[x])
file = list(filter(None, file))
file = ISA.RawURCL(file) #                  <------ Entry point 1, raw URCL
tvar = []
fixLabels(file)
file = list(filter(None, file))
file = countRegs(file)
repeat = True
while repeat:
    repeat = False
    replaceComplex(file)
    fixLabels(file)

file = ISA.CleanURCL(file) #                  <------ Entry point 2, modified URCL

print("\nURCL code:\n")
for y in range(0, len(file)):
    label = ""
    line = file[y].split(" ")
    try:
        ops = operands[line[0]]
    except:
        continue
    if line[0] == "IMPORT":
        continue
    elif line[0] == "BITS":
        if line[1] == ">=":
            if int(CPU_Stats["DATABUS_WIDTH"]) < int(line[2]):
                print(f"Your CPU does not meet the requirements for this program. Problem: Data bus too thin. (Minimum: {line[2]})")
        elif line[1] == "<=":
            if int(CPU_Stats["DATABUS_WIDTH"]) > int(line[2]):
                print(f"Your CPU does not meet the requirements for this program. Problem: Data bus too wide. (Maximum: {line[2]})")
        else:
            if int(CPU_Stats["DATABUS_WIDTH"]) != int(line[2]):
                print(f"Your CPU does not meet the requirements for this program. Problem: Data bus wrong width. (Must be {line[2]})")
        continue
    elif line[0] == "MINRAM":
        if int(CPU_Stats["MEMORY"]) < int(line[1]):
            print(f"Your CPU does not meet the requirements for this program. Problem: Not enough memory. (Must be {line[1]})")
        continue
    elif line[0] == "MINREG":
        if int(CPU_Stats["REGISTERS"]) < int(line[1]):
            print(f"Your CPU does not meet the requirements for this program. Problem: Not enough registers. (Must be {line[1]})")
        continue
    elif INS_Table[line[0]] == []:
        omitted += 1
        continue
    else:
        newlines = INS_Table[line[0]].copy()
    try:
        label = line[ops+1].strip()
        if label == "":
            sys.exit()
        elif label[:3] == "(__":
            labels[label[1:-1]] = len(code)
        else:
            labels[label.strip()[1:][:-1]] = len(code)
            label_list.append(label.strip()[1:][:-1])
    except:
        pass
    if ops != 0:
        for x in range(1, ops+1):
            if line[x][0] == "#":
                num = 0
                try:
                    if line[x][1] == "+":
                        num = int(line[x][2:])
                    elif line[x][1] == "-":
                        num = int(line[x][2:])*-1
                except:
                    pass
                    line[x] = str(int(CPU_Stats["DATABUS_WIDTH"])+num)
    newlines = INS_Table[line[0]].copy()
    length = len(code)
    for x in range(0, len(newlines)):
        newlines[x] = newlines[x].strip()
        for op in newlines[x].split(" "):
            if op[0] == "+":
                newlines[x] = newlines[x].replace(op, str(length+int(op[1:])))
            elif op[0] == "-":
                newlines[x] = newlines[x].replace(op, str(length-int(op[1:])))
        if ops > 0:
            newlines[x] = newlines[x].replace("<A>", line[1])
        if ops > 1:
            newlines[x] = newlines[x].replace("<B>", line[2])
        if ops > 2:
            newlines[x] = newlines[x].replace("<C>", line[3])
        if x == 0:
            newlines[x] += " " + label
            newlines[x] = newlines[x].strip()
        length += 1
    print(" ".join(line))
    for newline in newlines:
        if CPU_Stats["LINENUMS"]:
            code.append(str(len(code)).zfill(3) + ": " + newline)
        else:
            code.append(newline)
for lab in label_list:
    try:
        var.remove(lab)
    except:
        pass

code = ISA.LabelISA(code) #                  <------ Entry point 3, ISA with labels

label_list = list(filter(None, label_list))

for x in range(0, len(code)):
    for label in label_list:
        code[x] = code[x].replace(f"({label})", "")
        code[x] = code[x].replace(label, str(labels[label]))
if len(tvar) + len(var) > int(CPU_Stats["REGISTERS"]):
    print("\nWarning: You do not have enough registers to run this script. (Try using some memory instead?)")
print(f"\nVariables:           {var}")
tvar_copy = []
for var in tvar:
    if var not in tvar_copy:
        tvar_copy.append(var)
tvar = tvar_copy.copy()

code = ISA.FinalISA(code) #                  <------ Entry point 4, final ISA

print(f"Temporary variables: {tvar}")
print(f"# of unsupported instructions stripped: {omitted}")
print(f"\n{ISA_input} code:\n")
for line in code:
    print(line)
input()
