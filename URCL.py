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
labels = {
    }
branching_ops = ["BRP","BRN","BNZ","BRZ","BNC","BRC","BRA","BRL","BRG","BRE","BNE","BEV","BOD","BGE","BLE"]
operands = {"ADD":   3,"SUB":   3,"BSR":   3,"BSL":   3,"ADC":   3,"SBB":   3,"INC":   2,
            "DEC":   2,"MOV":   2,"IMM":   2,"XOR":   3,"AND":   3,"OR":    3,"NOR":   3,
            "NAND":  3,"XNOR":  3,"NOT":   2,"LOAD":  2,"STORE": 2,"BRA":   1,"BRC":   1,
            "BNC":   1,"BRZ":   1,"BNZ":   1,"BRN":   1,"BRP":   1,"NOP":   0,"HLT":   0,
            "MLT":   3,"DIV":   3,"MOD":   3,"SQRT":  2,"CAL":   1,"RET":   0,"PSH":   1,
            "POP":   1,"BRL":   3,"BRG":   3,"BRE":   3,"BNE":   3,"IN":    2,"OUT":   2,
            "BOD":   2,"BEV":   2,"RSH":   2,"LSH":   2,"CMP":   2,"SRS":   3,"BSS":   3,
            "BLE":   3,"BGE":   3}

fname = input("File to compile? ")+".txt"
try:
    f = open(fname)
    file = []
    for line in f:
        file.append(line)
    f.close()
except:
    print(f"'{fname}' does not exist. (Is it in a different folder?)")
    input()
    sys.exit()
omitted = 0

def snip(line):
    line = line.rstrip("\n")
    line = line.split("//")[0]
    line = line.strip()
    line = line.replace(",","")
    line = line.strip()
    return line

for x in range(0, len(file)):
    file[x] = snip(file[x])
    line = file[x].split(" ")
    try:
        ops = operands[line[0]]
    except:
        if line == "":
            continue
        if line[0][-1:] == ":":
            label = line[0][:-1]
            file[x+1] = snip(file[x+1]) + f" ({label})"
        else:
            file[x] = ""
    if line[0] in branching_ops:
        label = line[1]
        if label[0] == "+":
            file[x+int(label[1:])] = snip(file[x+int(label[1:])])
            file[x+int(label[1:])] += f" (__LABEL__#{count})"
        elif label[0] == "-":
            file[x-int(label[1:])] = snip(file[x-int(label[1:])])
            file[x-int(label[1:])] += f" (__LABEL__#{count})"
        else:
            continue
        file[x] = file[x].replace(label.strip(), f"__LABEL__#{count}")
        label = f"__LABEL__#{count}"
        label_list.append(label)
        count += 1

file = list(filter(None, file))

print("\nURCL code:\n")
for y in range(0, len(file)):
    label = ""
    line = file[y].split(" ")
    try:
        ops = operands[line[0]]
    except:
        continue
    if ISA_Table[line[0]] == []:
        omitted += 1
        continue
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
                if line[x][0] == "R":
                    line[x]= "$" + line[x][1:]
                if not line[x] in var:
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