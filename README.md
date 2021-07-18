# About URCL
URCL is a "Universal Redstone Computer Language", it's an intermediate language, so it isn't designed to be run on CPUs.
URCL compiles to a specified ISA using a Python config file.

# URCL Documentation
The URCL documentation can be found here: https://docs.google.com/spreadsheets/d/14u15VlSYORlt8EQu3C0ow0LTppoeio9gm2_z0Q4bOD8/edit?usp=sharing
Documentation for the beta version: https://docs.google.com/spreadsheets/d/1YAVlzYkib-YHJEu_x28qC4iXJDnM_YTvCKMBYrJXIT0

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

# Pragmas
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
```
@MWSP states that the stack pointer should be multi-word, if necessary.
@MWADDR states that memory addresses and memory pointers should be multi-word, if necessary.
@MWLABEL states that labels should be multi-word, if necessary.

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
 . Add translations written in your ISA for the ~25 core URCL instructions.
 . Fill in the CPU stats section with your CPU's specs.
If your CPU is more complex, you may also need to:
 . Make a custom function for replacing labels with absolute memory addresses. (For variable length instructions)
 . Make adjustments to the URCL / ISA code at different intervals to better suit your ISA with custom functions.