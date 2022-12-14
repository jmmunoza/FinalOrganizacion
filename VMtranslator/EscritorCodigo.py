
import os, os.path
from VMConstantes import *

# Traduce los comandos de VM y escribe un código Hack assembly

class CodeWriter(object):    
    def __init__(self, archivoSalida):
        self._out_file = open(archivoSalida, 'w')
        self._archivo_vm = ''
        self._labelnum = 0

    def __str__(self):
        pass
        
    def set_file_name(self, filename):
        self._archivo_vm, ext = os.path.splitext(filename)

    def close_file(self):
        self._out_file.close()
        
    def write_init(self):
        self._comando_tipo_A('256')
        self._comando_tipo_C('D', 'A')
        self._computo_a_registro(R_SP, 'D')         # SP=256
        self.write_call('Sys.init', 0)              # call Sys.init
        
    def write_arithmetic(self, comando):
        if   comando == 'add':  self._binario('D+A')
        elif comando == 'sub':  self._binario('A-D')
        elif comando == 'neg':  self._unuario('-D')
        elif comando == 'eq':   self._comparacion('JEQ')
        elif comando == 'gt':   self._comparacion('JGT')
        elif comando == 'lt':   self._comparacion('JLT')
        elif comando == 'and':  self._binario('D&A')
        elif comando == 'or':   self._binario('D|A')
        elif comando == 'not':  self._unuario('!D')
        
    def write_push_pop(self, comando, seg, index):
        if comando == C_PUSH:   self._push(seg, index)
        elif comando == C_POP:  self._pop(seg, index)

    def write_label(self, label):
        self._l_comando(label)
        
    def write_goto(self, label):
        self._comando_tipo_A(label)              # A=label
        self._comando_tipo_C(None, '0', 'JMP')   # 0;JMP
        
    def write_if(self, label):
        self._pop_a_destino('D')              # D=*SP
        self._comando_tipo_A(label)              # A=label
        self._comando_tipo_C(None, 'D', 'JNE')   # D;JNE
        
    def write_call(self, function_name, num_args):
        return_address = self._new_label()
        self._push(S_CONST, return_address) # push return_address
        self._push(S_REG, R_LCL)            # push LCL
        self._push(S_REG, R_ARG)            # push ARG
        self._push(S_REG, R_THIS)           # push THIS
        self._push(S_REG, R_THAT)           # push THAT
        self._load_sp_offset(-num_args-5)
        self._computo_a_registro(R_ARG, 'D')       # ARG=SP-n-5
        self._registro_a_reg(R_LCL, R_SP)       # LCL=SP
        self._comando_tipo_A(function_name)      # A=function_name
        self._comando_tipo_C(None, '0', 'JMP')   # 0;JMP
        self._l_comando(return_address)     # (return_address)
        
    def write_return(self):
        self._registro_a_reg(R_FRAME, R_LCL)    # R_FRAME = R_LCL
        self._comando_tipo_A('5')                # A=5
        self._comando_tipo_C('A', 'D-A')         # A=FRAME-5
        self._comando_tipo_C('D', 'M')           # D=M
        self._computo_a_registro(R_RET, 'D')       # RET=*(FRAME-5)
        self._pop(S_ARG, 0)                 # *ARG=return value
        self._reg_a_destino('D', R_ARG)       # D=ARG
        self._computo_a_registro(R_SP, 'D+1')      # SP=ARG+1
        self._prev_frame_a_reg(R_THAT)     # THAT=*(FRAME-1)
        self._prev_frame_a_reg(R_THIS)     # THIS=*(FRAME-2)
        self._prev_frame_a_reg(R_ARG)      # ARG=*(FRAME-3)
        self._prev_frame_a_reg(R_LCL)      # LCL=*(FRAME-4)
        self._reg_a_destino('A', R_RET)       # A=RET
        self._comando_tipo_C(None, '0', 'JMP')   # goto RET
        
    def _prev_frame_a_reg(self, reg):
        self._reg_a_destino('D', R_FRAME)     # D=FRAME
        self._comando_tipo_C('D', 'D-1')         # D=FRAME-1
        self._computo_a_registro(R_FRAME, 'D')     # FRAME=FRAME-1
        self._comando_tipo_C('A', 'D')           # A=FRAME-1
        self._comando_tipo_C('D', 'M')           # D=*(FRAME-1)
        self._computo_a_registro(reg, 'D')         # reg=D
        
    def write_function(self, function_name, num_locals):
        self._l_comando(function_name)
        for i in range(num_locals):
            self._push(S_CONST, 0)
        
    # Generate code for push and pop
    def _push(self, seg, index):
        if   self._is_const_seg(seg):   self._val_a_stack(str(index))
        elif self._is_mem_seg(seg):     self._mem_a_stack(self._asm_mem_seg(seg), index)
        elif self._is_reg_seg(seg):     self._reg_a_stack(seg, index)
        elif self._is_static_seg(seg):  self._static_a_stack(seg, index)
        self._inc_sp()

    def _pop(self, seg, index):
        self._dec_sp()
        if   self._is_mem_seg(seg):     self._stack_a_mem(self._asm_mem_seg(seg), index)
        elif self._is_reg_seg(seg):     self._stack_a_reg(seg, index)
        elif self._is_static_seg(seg):  self._stack_a_static(seg, index)

    def _pop_a_destino(self, dest):
        self._dec_sp()
        self._stack_a_destino(dest)           # dest=*SP

    # Types of segments
    def _is_mem_seg(self, seg):
        return seg in [S_LCL, S_ARG, S_THIS, S_THAT]
        
    def _is_reg_seg(self, seg):
        return seg in [S_REG, S_PTR, S_TEMP]

    def _is_static_seg(self, seg):
        return seg == S_STATIC

    def _is_const_seg(self, seg):
        return seg == S_CONST

    # Generate code for arithmetic and logic operations.
    # Pop args off stack, perform an operation, and push the result on the stack
    def _unuario(self, comp):
        self._dec_sp()                      # --SP
        self._stack_a_destino('D')            # D=*SP
        self._comando_tipo_C('D', comp)          # D=COMP
        self._comp_a_stack('D')            # *SP=D
        self._inc_sp()                      # ++SP
        
    def _binario(self, comp):
        self._dec_sp()                      # --SP
        self._stack_a_destino('D')            # D=*SP
        self._dec_sp()                      # --SP
        self._stack_a_destino('A')            # A=*SP
        self._comando_tipo_C('D', comp)          # D=comp
        self._comp_a_stack('D')            # *SP=D
        self._inc_sp()                      # ++SP

    def _comparacion(self, jump):
        self._dec_sp()                      # --SP
        self._stack_a_destino('D')            # D=*SP
        self._dec_sp()                      # --SP
        self._stack_a_destino('A')            # A=*SP
        self._comando_tipo_C('D', 'A-D')         # D=A-D
        label_eq = self._jump('D', jump)    # D;jump to label_eq
        self._comp_a_stack('0')            # *SP=0
        label_ne = self._jump('0', 'JMP')   # 0;JMP to label_ne
        self._l_comando(label_eq)           # (label_eq)
        self._comp_a_stack('-1')           # *SP=-1
        self._l_comando(label_ne)           # (label_ne)
        self._inc_sp()                      # ++SP

    # SP operations
    def _inc_sp(self):
        self._comando_tipo_A('SP')               # A=&SP
        self._comando_tipo_C('M', 'M+1')         # SP=SP+1
        
    def _dec_sp(self):
        self._comando_tipo_A('SP')               # A=&SP
        self._comando_tipo_C('M', 'M-1')         # SP=SP-1

    def _load_sp(self):
        self._comando_tipo_A('SP')               # A=&SP
        self._comando_tipo_C('A', 'M')           # A=SP

    # Methods to store values onto the stack        
    def _val_a_stack(self, val):
        self._comando_tipo_A(val)                # A=val
        self._comando_tipo_C('D', 'A')           # D=A
        self._comp_a_stack('D')            # *SP=D

    def _reg_a_stack(self, seg, index):
        self._reg_a_destino('D', self._reg_num(seg, index))   # D=R#
        self._comp_a_stack('D')                            # *SP=D
        
    def _mem_a_stack(self, seg, index, indir=True):
        self._load_seg(seg, index, indir)   # A=seg+index
        self._comando_tipo_C('D', 'M')           # D=*(seg+index)
        self._comp_a_stack('D')            # *SP=*(seg+index)

    def _static_a_stack(self, seg, index):
        self._comando_tipo_A(self._static_name(index))   # A=&func.#
        self._comando_tipo_C('D', 'M')                   # D=func.#
        self._comp_a_stack('D')                    # *SP=func.#
        
    def _comp_a_stack(self, comp):
        self._load_sp()
        self._comando_tipo_C('M', comp)          # *SP=comp

    # Methods to retrieve values from the stack
    def _stack_a_reg(self, seg, index):
        self._stack_a_destino('D')            # D=*SP
        self._computo_a_registro(self._reg_num(seg, index), 'D')

    def _stack_a_mem(self, seg, index, indir=True):
        self._load_seg(seg, index, indir)
        self._computo_a_registro(R_COPY, 'D')      # R_COPY=D
        self._stack_a_destino('D')            # D=*SP
        self._reg_a_destino('A', R_COPY)      # A=R_COPY
        self._comando_tipo_C('M', 'D')           # *(seg+index)=D

    def _stack_a_static(self, seg, index):
        self._stack_a_destino('D')
        self._comando_tipo_A(self._static_name(index))
        self._comando_tipo_C('M', 'D')

    def _stack_a_destino(self, dest):
        self._load_sp()
        self._comando_tipo_C(dest, 'M')          # dest=*SP

    # Calculate SP+/-offset
    def _load_sp_offset(self, offset):
        self._load_seg(self._asm_reg(R_SP), offset)

    # load address of seg+index into A and D registers
    def _load_seg(self, seg, index, indir=True):
        if index == 0:
            self._load_seg_no_index(seg, indir)
        else:
            self._load_seg_index(seg, index, indir)

    def _load_seg_no_index(self, seg, indir):
        self._comando_tipo_A(seg)            # A=seg
        if indir: self._indir(dest='AD')# A=D=*A

    def _load_seg_index(self, seg, index, indir):
        comp = 'D+A'
        if index < 0:
            index = -index
            comp = 'A-D'
        self._comando_tipo_A(str(index))     # A=index
        self._comando_tipo_C('D', 'A')       # D=A
        self._comando_tipo_A(seg)            # A=seg
        if indir: self._indir()         # A=*seg
        self._comando_tipo_C('AD', comp)     # A=D=seg+/-index
    
    # Register ops
    def _reg_a_destino(self, dest, reg):
        self._comando_tipo_A(self._asm_reg(reg)) # @R#
        self._comando_tipo_C(dest, 'M')          # dest=R#

    def _computo_a_registro(self, reg, comp):
        self._comando_tipo_A(self._asm_reg(reg)) # @R#
        self._comando_tipo_C('M', comp)          # R#=comp

    def _registro_a_reg(self, dest, src):
        self._reg_a_destino('D', src)
        self._computo_a_registro(dest, 'D')        # Rdest = Rsrc

    def _indir(self, dest='A'):
        self._comando_tipo_C(dest, 'M')
        
    def _reg_num(self, seg, index):
        return self._reg_base(seg)+index
        
    def _reg_base(self, seg):
        reg_base = {'reg':R_R0, 'pointer':R_PTR, 'temp':R_TEMP}
        return reg_base[seg]
        
    def _static_name(self, index):
        return self._archivo_vm+'.'+str(index)
        
    # Assembler names for segments/registers
    def _asm_mem_seg(self, seg):
        asm_label = {S_LCL:'LCL', S_ARG:'ARG', S_THIS:'THIS', S_THAT:'THAT'}
        return asm_label[seg]

    def _asm_reg(self, regnum):
        return 'R'+str(regnum)
        
    # Jump to a new label and return the label for later definition
    def _jump(self, comp, jump):
        label = self._new_label()
        self._comando_tipo_A(label)              # A=label
        self._comando_tipo_C(None, comp, jump)   # comp;jump
        return label
    
    # Generate a new label    
    def _new_label(self):
        self._labelnum += 1
        return 'LABEL'+str(self._labelnum)
    
    # Write an assembler @ comando   
    def _comando_tipo_A(self, address):
        self._out_file.write('@'+address+'\n')
        
    # Write an assembler C comando
    def _comando_tipo_C(self, dest, comp, jump=None):
        if dest != None:
            self._out_file.write(dest+'=')
        self._out_file.write(comp)
        if jump != None:
            self._out_file.write(';'+jump)
        self._out_file.write('\n')
        
    # Write an assembler L comando
    def _l_comando(self, label):
        self._out_file.write('('+label+')\n')