# URCL
URCL is a "Universal Redstone Computer Language", it's an intermediate language, so it isn't designed to be run on CPUs. URCL compiles to a specified ISA using a custom config file. 
# Documentation
The URCL documentation can be found here: https://docs.google.com/spreadsheets/d/14u15VlSYORlt8EQu3C0ow0LTppoeio9gm2_z0Q4bOD8/edit?usp=sharing
# Can't you just go from a Universal ISA -> binary -> platform?
Well to start off with, we can't have universal binary because CPUs all have different bus widths, opcodes etc. There is way too much variance.
We can't have a universal ISA because there are too many URCL instructions, and the opcode would be too large. Also, there is still too much variance for this to be viable.
So that leaves the level we're on now - an intermediate language that compiles down to an ISA, not designed to be run directly.
