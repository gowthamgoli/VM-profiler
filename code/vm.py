import sys
from collections import OrderedDict
from collections import defaultdict
from pprint import pprint
from subroutines import *
from helpers import *

class MainMemory():
	registers = {'eax':0, 'ebx':0,'ecx':0, 'edx':0, 'esi':0, 'edi':0, 'esp':0, 'ebp':0, 'eip':0, 'r08':0, 'r09':0, 'r10':0, 'r11':0, 'r12':0, 'r13':0, 'r14':0, 'r15':0, 'flags':0, 'rem':0}
	addresses = defaultdict(int)
	stack = []

class ProgramCounter():
	inst_num = 0		#inst num within the label
	curr_label = None	#current label being executed
	labels = []			#list of labels acc. to the order in which they appear in the code
	label_index = 0		#index of the current label being executed
	instructions = OrderedDict()
	jump_flag = True

class Blocks():
	basiblocks = {}


instruction = {'op': None, 'arg0': None, 'arg1': None}


call_subroutine = {'mov':mov, 'push':push, 'pop':pop, 'pushf':pushf, 'popf':popf, 'call':call, 'ret':ret, 'inc':inc, 'dec':dec, 'add':add, 'sub':sub,\
				   'mul':mul, 'div':div, 'mod':mod, 'rem':rem, 'not':binnot, 'xor':binxor, 'or':binor, 'and':binand, 'shl':binshl, 'shr':binshr, 'cmp':cmpr,\
				   'jmp':jmp, 'je':je, 'jne':jne, 'jg':jg, 'jge':jge, 'jl':jl, 'jle':jle, 'prn':prn}


def parseFile(filename, pc):
	lines = open(filename,'r').read().split('\n')
	#print lines
	currLabel = 'Null'
	pc.instructions[currLabel] = []
	counter = 0
	line = ''
	for line in lines:
		if line.strip().startswith('#') or not line or line.isspace():
			continue
		if ':' in line:
			tokens = line.split(':')
			if currLabel!='Null' and pc.instructions[currLabel] == []:
				pc.instructions[currLabel] = [('', counter)]
				counter += 1
			currLabel = tokens[0]+':'
			pc.instructions[currLabel] = []
			#counter += 1
			if len(tokens) == 2:
				line = tokens[1]
		if not ':' in line:
			line = line.strip()
			#print line
			if line:
				line = line.split('#')[0].strip()
				pc.instructions[currLabel].append((line, counter))
				counter += 1

	if pc.instructions[currLabel] == []:
			pc.instructions[currLabel] = [('', counter)]
			#counter += 1

	if not pc.instructions['Null']: del pc.instructions['Null']


	for label in pc.instructions:
		pc.labels.append(label)
		'''print label
		for inst in pc.instructions[label]:
			print inst'''

def main():
	filename = sys.argv[1]

	mainMemory = MainMemory()
	pc = ProgramCounter()
	blocks = Blocks()


	#parses file and adds insts to the dict 'instructions' to the form of {label:[inst]}
	parseFile(filename, pc)
	print pc.instructions

	#print pc.labels
	#represesnts the current instruction number within that label
	pc.inst_num = 0

	if 'start:' in pc.labels:
		pc.curr_label = 'start:'
		pc.label_index = pc.labels.index('start:')
	else:
		pc.curr_label = pc.labels[0]

	set_leaders_next_to_jump(pc, blocks)

	#Keep executing until we reach the last instrunction of the current label
	while pc.inst_num != len(pc.instructions[pc.curr_label]):
		#get current instructions
		curr_inst = pc.instructions[pc.curr_label][pc.inst_num][0]
		num = pc.instructions[pc.curr_label][pc.inst_num][1]

		#print curr_inst
		#print pc.curr_label, pc.inst_num

		if pc.jump_flag:
			if (pc.curr_label, pc.inst_num, num) in blocks.basiblocks:
				blocks.basiblocks[((pc.curr_label, pc.inst_num, num))] += 1
			else:
				blocks.basiblocks[((pc.curr_label, pc.inst_num, num))] = 1
			#print 'beginning block (' + pc.curr_label + curr_inst + ')'
		pc.jump_flag = False

		if curr_inst:

			tokens = curr_inst.split(None, 1)

			#get the op code
			instruction['op'] = tokens[0]

			#get the arguments
			if len(tokens) == 2:
				args = [item.strip() for item in tokens[1].split(',')]
				if args:
					instruction['arg0'] = args[0]
					instruction['arg1'] = args[1] if len(args) == 2 else None
			else:
				instruction['arg0'] = None
				instruction['arg1'] = None

			#print args

			call_subroutine[instruction['op']](instruction['arg0'], instruction['arg1'], mainMemory, pc)
			#pprint(mainMemory.registers)
			#pprint(mainMemory.addresses)
			#print MainMemory.stack
			#print ''

		pc.inst_num += 1
		#check if we reached the last intruction of the current label
		if pc.inst_num == len(pc.instructions[pc.curr_label]):

			#go to next label
			pc.label_index += 1
			#if the current label is the last label in the sequence of the labels in the code then break out of loop
			if pc.label_index == len(pc.labels): break
			pc.curr_label = pc.labels[pc.label_index]
			pc.inst_num = 0
	#print blocks.basiblocks
	#for k in blocks.basiblocks:
	#		print k[2]
	blocks.basiblocks = OrderedDict(sorted(blocks.basiblocks.items(),key = lambda e:e[0][2]))
	#print blocks.basiblocks

	insts = pc.instructions.items()
	blks = blocks.basiblocks.items()
	print ''
	print insts
	print '' 
	print blks
	
	i = 0
	k = 0

	for i in range(0, len(blks)-1):
		beginLabel = blks[i][0][0]
		beginInd = blks[i][0][1]
		endLabel = blks[i+1][0][0]
		endInd = blks[i+1][0][1]
		flag = True
		'''print ''
		print 'beginLabel: '+str(beginLabel)
		print 'beginInd: '+str(beginInd)
		print 'endLabel: '+str(endLabel)
		print 'endInd: '+str(endInd)
		print 'k: ' + str(k)
		print '''

		frequency = blks[i][1]
		
		print frequency

		if beginLabel == endLabel:
			for p in range(beginInd, endInd):
				print insts[k][1][p][0]
			print ''
			continue

		while insts[k][0] != endLabel:
			#print 'k: ' + str(k)
			print 'currLabel:' + insts[k][0]
			if flag:
				for p in range(beginInd, len(insts[k][1])):
					print insts[k][1][p][0] 
				flag = False
			else:
				for inst in insts[k][1]:
					if inst[0]: print inst[0]
			k += 1

		if insts[k][0] == endLabel:
			for p in range(0, endInd):
				print insts[k][1][p][0]
			#k += 1
		print ''
	
	beginInd = blks[i+1][0][1]
	frequency = blks[i][1]
	print frequency
	k = len(insts)-1
	for p in range(beginInd, len(insts[k][1])):
		print insts[k][1][p][0] 
		


		


	#print instList




if __name__ == "__main__":
    main()