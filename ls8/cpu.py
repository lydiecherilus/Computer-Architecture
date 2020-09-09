"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # Hold 256 bytes of memory 
        self.reg = [0] * 8 # Hold 8 general-purpose registers
        self.reg[7] = 0xF4
        self.pc = 0 # program counter
        self.branch_table = {
            0b10000010: self.LDI,  # Load / Set a specified register to a specified value
            0b01000111: self.PRN,  # Print numeric value store in a register
            0b00000001: self.HLT,  # Halt the CPU and exit the emulator
            0b10100010: self.MUL,  # multiply
            0b01000101: self.PUSH,
            0b01000110: self.POP,
        }

    # MAR: Memory Address Register, holds the memory address we're reading or writing
    # MDR: Memory Data Register, holds the value to write or the value just read
    # Accept the address to read and return the value stored there
    def ram_read(self, MAR):
        return self.ram[MAR]

    # Accept a value to write, and the address to write it to
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def LDI(self): 
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        self.reg[operand_a] = operand_b
        self.pc += 3
   
    def PRN(self): 
        operand_a = self.ram_read(self.pc + 1)
        print(self.reg[operand_a])
        self.pc += 2

    def HLT(self): 
        sys.exit()
        self.pc += 1

    def MUL(self): 
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        result = self.reg[operand_a] * self.reg[operand_b]
        print(result)
        self.pc += 3

    def PUSH(self): 
        given_register = self.ram[self.pc + 1]
        value_in_register = self.reg[given_register]
        # decrement the stack pointer
        self.reg[7] -= 1
        # write the value at the given register to memory at the stack pointer location
        self.ram[self.reg[7]] = value_in_register
        self.pc += 2

    def POP(self): 
        given_register = self.ram[self.pc + 1]
        # write the value in memory at the top of the stack to the given register
        value_from_memory = self.ram[self.reg[7]]
        self.reg[given_register ] = value_from_memory
        # increment the stack pointer
        self.reg[7] += 1
        self.pc += 2
  
    def load(self):
        """Load a program into memory."""
  
        if len(sys.argv) < 2:
            print('second filename missing')
            sys.exit(1)
    
        filename = sys.argv[1]
        try:  
            address = 0
            with open(filename) as file:
                for line in file:
                    split_line = line.split('#') # split line on # symbol
                    code_value = split_line[0].strip() # remove white space and /n character
                    if code_value == '':
                        continue
                    instruction = int(code_value, 2)
                    self.ram[address] = instruction
                    address += 1
        except FileNotFoundError:
            print(f'{sys.argv[1]} file not found')
            sys.exit(2)

        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            IR = self.ram[self.pc] # IR: Instruction Register, contains a copy of the currently executing instruction
            if IR in self.branch_table:
                self.branch_table[IR]()

# cd ls8 
# py -3 ls8.py  examples/print8.ls8
# py -3 ls8.py  examples/mult.ls8
# py -3 ls8.py  examples/stack.ls8