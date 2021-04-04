# About URCL
URCL is a "Universal Redstone Computer Language", it's an intermediate language, so it isn't designed to be run on CPUs.
URCL compiles to a specified ISA using a Python config file.

# URCL Documentation
The URCL documentation can be found here: https://docs.google.com/spreadsheets/d/14u15VlSYORlt8EQu3C0ow0LTppoeio9gm2_z0Q4bOD8/edit?usp=sharing
Documentation for the beta version: https://docs.google.com/spreadsheets/d/1YAVlzYkib-YHJEu_x28qC4iXJDnM_YTvCKMBYrJXIT0

# What it does
You can think of this is a framework to help you easily compile URCL to your ISA without starting from the ground up.
It does the vast majority of the work, and only leaves you to do CPU-specific parts.
Here's a list of things the compiler does for you:
 . Converts all constants and bit patterns to base-10.
 . Replaces all relative addresses with labels.
 . Replaces unsupported complex instructions with supported core instructions.
 . Expands function calls, ensuring register preservation.
 . Optimises the URCL code where possible, using memory instead of the stack in some cases.

# How to get URCL -> <your ISA> compiler working
There's an ExampleISA.py config file provided, this is roughly what a config file will look like, based off my own HPU4 instruction set.
There is also a Template.py config file provided, this is a blank config file ready to be filled in.
Here's a list of things you need to do to support URCL:
 . Add translations written in your ISA for the ~25 core URCL instructions.
 . Fill in the CPU stats section with your CPU's specs.
If your CPU is more complex, you may also need to:
 . Make a custom function for replacing labels with absolute memory addresses. (For variable length instructions)
 . Make adjustments to the URCL / ISA code at different intervals to better suit your ISA with custom functions.