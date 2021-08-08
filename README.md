# About URCL
URCL is a "Universal Redstone Computer Language", it's an intermediate language, so it isn't designed to be run on CPUs.
URCL compiles to a specified ISA using a Python config file.

# URCL Documentation
The URCL documentation can be found here: https://docs.google.com/spreadsheets/d/1YAVlzYkib-YHJEu_x28qC4iXJDnM_YTvCKMBYrJXIT0

# Usage
To run the file via the command line, you can do:
```
py URCL.py <myISA> <programName.urcl> <ISAoutput.txt> <URCLoutput.urcl>
```
You may also exclude parameters from right to left, so you can have a custom ISA output file without a custom URCL output for example.
You may also run the file without any parameters by simply entering:
```
py URCL.py
```
Additionally, you can use the special `Emulate` ISA to just use the URCL-simplification feature.
Similarly, the special `Core` ISA produces code consisting of only core instructions.
The resulting code can be used with the included `URCL_Emulator.py`, which allows you to test the URCL program to find any bugs.
```
py URCL_emulator.py <bits> <URCLoutput.urcl>
```
The `<bits>` parameter is optional, as is `<URCLoutput.urcl>`.
As with URCL.py, you cannot have `<URCLoutput.urcl>` without specifying `<bits>`.

# Pragmas and other unofficial addons
You can have a single character string as an immediate. The ascii value will be used:
```
IMM $1 "A" // 'A' is also valid
```
Will become:
```
IMM $1 65
```
Control characters can be used with this system too, these are:
```
"\n"  / ASCII 10 / new line
"\CR" / ASCII 13 / go to the start of the line
"\LF" / ASCII 10 / same as "/n"
"\BS" / ASCII 8  / backspace
"\SP" / ASCII 32 / space
```

There are some pragmas specific to this compiler which I have defined, these are not official, but they are used as follows:
```
@PTR {reg}
  {code where reg is used as a pointer}
@UNPTR {reg}
```
This defines a register as a pointer, which means if multiword addressing is enabled and used, this register may be treated in a special way.
Pointers can only be used in: ADD, SUB, INC, DEC, IMM, MOV, LOD, STR, LLOD, LSTR.
```
@MWSP
@MWADDR
@MWLABEL
@MWFULL
```
@MWSP states that the stack pointer should be multi-word, if necessary.
@MWADDR states that memory addresses and memory pointers should be multi-word, if necessary.
@MWLABEL states that labels should be multi-word, if necessary.
@MWFULL is **full** multiword. This means a 1-bit CPU could run a program like this:
```
BITS 16
IMM $1 2000
IMM $2 3000
MLT $3 $2 $1
OUT %NUMB $3
```
Note that because I don't have multi-word translations for all instructions, @MWFULL programs will end up being very long.

# What it does
You can think of this is a framework to help you easily compile URCL to your ISA without starting from the ground up.
It does the vast majority of the work, and only leaves you to do CPU-specific parts.
Here's a list of things the compiler does for you:
 . Converts all constants and bit patterns to base-10.
 . Replaces all relative addresses with labels.
 . Replaces unsupported complex instructions with supported core instructions.
 . Optional multi-word support.

# How to get a URCL -> your ISA compiler working
There's an ExampleISA.py config file provided, this is roughly what a config file will look like, based off my own HPU4 instruction set.
There is also a Template.py config file provided, this is a blank config file ready to be filled in.
Here's a list of things you need to do to support URCL:
 . Add translations written in your ISA for the 7 core URCL instructions.
 . Fill in the CPU stats section with your CPU's specs.
If your CPU is more complex, you may also need to:
 . Make a custom function for replacing labels with absolute memory addresses. (For variable length instructions)
 . Make adjustments to the URCL / ISA code at different intervals to better suit your ISA with custom functions.