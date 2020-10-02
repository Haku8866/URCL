import json
import sys
ISA = input("Compile to which ISA? ")+".json"
try:
    f = open(ISA) 
    ISA_Table = json.load(f)
    f.close()
except:
    print("File not found or file is invalid. (Is it in a different folder?)")
    input()
    sys.exit()

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
            "BLE":   3,"BGE":   3,"BITS":  2,"MINREG":1,"MINRAM":1,"IMPORT":0}

cmplx_subs = {
    "MLT": ["IMM <A> 0","BEV +2 <C>","ADD <A> <A> <B>","LSH <B> <B>","RSH <C> <C>","BNZ -4"],
    "DIV": [],
    "MOD": [],
    "CAL": [],
    "RET": [],
    "PSH": [],
    "POP": [],
    "BRL": [],
    "BRG": [],
    "BRE": [],
    "BNE": [],
    "BOD": [],
    "BEV": [],
    "BLE": [],
    "BGE": [],
    "IN":  [],
    "OUT": [],
    "BSR": [],
    "BSL": [],
    "SRS": [],
    "BSS": [],
    "CMP": [],
    "ADC": [],
    "SBB": [],
    }

''' BSR CODE TO BE IMPLEMENTED AFTER TEMPORARY VARIABLES ARE SUPPORTED
            //BSR $A $B $C
MOV $X <C>  //set X to C
MOV <A> <B> //copy B to A
RSH <A> <A> //shift A right
DEC $X      //decrement counter
BNZ -2      //if not done, loop
'''

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

file = list(filter(None, file))
omitted = 0

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
            elif char not in "#+-$: ":
                striplist.append(char)
        if striplist != []:
            for char in striplist:
                line[x] = line[x].replace(char,"")
    line = " ".join(line)
    return line

for x in range(0, len(file)):
    file[x] = snip(file[x])
file = list(filter(None, file))
def fixLabels(file):
    global count
    for x in range(0, len(file)):
        line = file[x].split(" ")
        try:
            ops = operands[line[0]]
        except:
            if line == "":
                continue
            if line[0][-1:] == ":":
                label = line[0][:-1]
                file[x+1] += f" ({label})"
            else:
                file[x] = ""
        if line[0] in branching_ops:
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

def replaceComplex(file):
    for x in range(0, len(file)):
        line = file[x].split()
        if line[0] == "BITS" or line[0] == "IMPORT" or line[0] == "MINREG" or line[0] == "MINRAM":
            continue
        if ISA_Table[line[0]] == []:
            if cmplx_subs[line[0]] != []:
                repeat = True
                newlines = cmplx_subs[line[0]]
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
                newlines.reverse()
                file.pop(x)
                for newline in newlines:
                    file.insert(x, newline)

file = list(filter(None, file))
fixLabels(file)
repeat = True
while repeat:
    repeat = False
    replaceComplex(file)
    fixLabels(file)
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
            if int(ISA_Table["DATABUS_WIDTH"]) < int(line[2]):
                print(f"Your CPU does not meet the requirements for this program. Problem: Data bus too thin. (Minimum: {line[2]})")
                input()
                sys.exit()
        elif line[1] == "<=":
            if int(ISA_Table["DATABUS_WIDTH"]) > int(line[2]):
                print(f"Your CPU does not meet the requirements for this program. Problem: Data bus too wide. (Maximum: {line[2]})")
                input()
                sys.exit()
        else:
            if int(ISA_Table["DATABUS_WIDTH"]) != int(line[2]):
                print(f"Your CPU does not meet the requirements for this program. Problem: Data bus wrong width. (Must be {line[2]})")
                input()
                sys.exit()
        continue
    elif line[0] == "MINRAM":
        if int(ISA_Table["MEMORY"]) < int(line[1]):
            print(f"Your CPU does not meet the requirements for this program. Problem: Not enough memory. (Must be {line[1]})")
            input()
            sys.exit()
        continue
    elif line[0] == "MINREG":
        if int(ISA_Table["REGISTERS"]) < int(line[1]):
            print(f"Your CPU does not meet the requirements for this program. Problem: Not enough registers. (Must be {line[1]})")
            input()
            sys.exit()
        continue
    elif ISA_Table[line[0]] == []:
        omitted += 1
        continue
    else:
        newlines = ISA_Table[line[0]].copy()
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
            try:
                int(line[x])
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
                    line[x] = str(int(ISA_Table["DATABUS_WIDTH"])+num)
                elif line[x][0] == "R":
                    line[x]= "$" + line[x][1:]
                if not line[x] in var:
                    try:
                        int(line[x])
                    except:
                        var.append(line[x])
    newlines = ISA_Table[line[0]].copy()
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
        if ISA_Table["LINENUMS"]:
            code.append(str(len(code)).zfill(3) + ": " + newline)
        else:
            code.append(newline)
for lab in label_list:
    try:
        var.remove(lab)
    except:
        pass

label_list = list(filter(None, label_list))

for x in range(0, len(code)):
    for label in label_list:
        code[x] = code[x].replace(f"({label})", "")
        code[x] = code[x].replace(label, str(labels[label]))
print(f"\nVariables: {var}")
print(f"# of unsupported instructions stripped: {omitted}")
print(f"\n{ISA[:-5]} code:\n")
if ISA_Table["AFTEREFFECT"] != "":
    try:
        exec(ISA_Table["AFTEREFFECT"])
    except:
        print("After effect failed. (Contact ISA designer.)")
        input()
        sys.exit()

for line in code:
    print(line)
input()
