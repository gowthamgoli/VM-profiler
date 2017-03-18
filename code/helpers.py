#from sys import getsizeof
LEN = 32
MAX = 2147483647
MIN = -2147483648

def is_mem_address(x):
	if len(x) <= 2:	return False
	if x[0] == '[' and x[-1] == ']': return True
	return False

def is_number(x):
	if x.isdigit():	return True
	if x[0] == '-' and x[1:].isdigit(): return True
	if x[0] == '+' and x[1:].isdigit(): return True
	if len(x) >= 3:
		if (x[0] == '0' and x[1] == 'x') or (x[-2] == '|' and x[-1] == 'h') or (x[-2] == '|' and x[-1] == 'b'): return True
	return False

def is_register(x, registers):
	if x in registers: return True
	return False

def get_value_mem(x, addresses):
	x = get_value_num(x[1:-1])
	return addresses[x]

def get_value_num(x):
	if x.isdigit():	return int(x)
	if x[0] == '-' and x[1:].isdigit(): return -1*int(x[1:])
	if x[0] == '+' and x[1:].isdigit(): return int(x[1:])
	if (x[0] == '0' and x[1] == 'x'):	return int(x[2:], 16)
	if (x[-2] == '|' and x[-1] == 'h'):	return int(x[:-2], 16)
	if (x[-2] == '|' and x[-1] == 'b'):	return int(x[:-2], 2)

def get_value_reg(x, registers):
	return registers[x] 

def get_label_inst_num(x, pc):
	count = 0
	label = ''
	for label in pc.labels:
		count += len(pc.instructions[label])
		if x < count:
			return label, x - count + len(pc.instructions[label])



def store_val(x, val, mainMemory):
	while val > MAX or val < MIN:
		if val > MAX:
			val = val - 2**32
		else:
			val = 2**32 + val
	#if val > 2**32:
	#	exit()
	if is_mem_address(x):
		mainMemory.addresses[get_value_num(x[1:-1])] = val
	elif is_register(x, mainMemory.registers):
		mainMemory.registers[x] = val

def get_value(arg, mainMemory):
	#print 'in get value'
	if is_mem_address(arg):
		#print 'its a mem address'
		return get_value_mem(arg, mainMemory.addresses)
	elif is_number(arg):
		#print 'its a number'
		return get_value_num(arg)
	elif is_register(arg, mainMemory.registers):
		#print 'its a register'
		return get_value_reg(arg, mainMemory.registers)
	#else:
		return 'x'

def set_leaders_next_to_jump(pc, blocks):
	jumps = {'call', 'ret', 'jmp', 'jmp', 'je', 'jne', 'jg', 'jge', 'jl', 'jle'}
	#print pc.instructions
	opcode = ''
	isPrevinstJump = False
	for label in pc.labels:
		count = len(pc.instructions[label])
		for i in range(0, count):
			curr_inst = pc.instructions[label][i][0]
			num = pc.instructions[label][i][1]
			if isPrevinstJump:
				blocks.basiblocks[(label, i, num)] = 0 
			opcode = curr_inst.split(None, 1)[0] if curr_inst else ''
			isPrevinstJump = True if opcode in jumps else False
	print blocks.basiblocks


#is_mem_address('100|b')