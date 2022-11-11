#programa general que traduce codigos en VM a ASM

import sys, os, os.path, glob
import Parser, EscritorCodigo
from VMConstantes import *

class VMTraductor(object):
    def __init__(self):
        pass
        
    def traducir_VM(self, archivosEntrada, archivoSalida):
        if archivosEntrada != []:
            code_writer = EscritorCodigo.CodeWriter(archivoSalida)
            code_writer.write_init()
            print(f'..lista de archivos VM a procesar:: Cantidad: {len(archivosEntrada)} -> {archivosEntrada}')
            for archivoEntrada in archivosEntrada:
                self._translate(archivoEntrada, code_writer)
            code_writer.close_file()
        
    def _translate(self, archivoEntrada, code_writer):
        parser = Parser.Parser(archivoEntrada)
        code_writer.set_file_name(os.path.basename(archivoEntrada))
        while parser.has_more_commands():
            parser.advance()
            self._gen_code(parser, code_writer)
            
    def _gen_code(self, parser, code_writer):
        cmd = parser.command_type()
        if cmd == C_ARITHMETIC:
            code_writer.write_arithmetic(parser.arg1())
        elif cmd == C_PUSH or cmd == C_POP:
            code_writer.write_push_pop(cmd, parser.arg1(), parser.arg2())
        elif cmd == C_LABEL:
            code_writer.write_label(parser.arg1())
        elif cmd == C_GOTO:
            code_writer.write_goto(parser.arg1())
        elif cmd == C_IF:
            code_writer.write_if(parser.arg1())
        elif cmd == C_FUNCTION:
            code_writer.write_function(parser.arg1(), parser.arg2())
        elif cmd == C_RETURN:
            code_writer.write_return()
        elif cmd == C_CALL:
            code_writer.write_call(parser.arg1(), parser.arg2())

def get_files( file_or_dir ):
    if file_or_dir.endswith('.vm'):
        return [file_or_dir], file_or_dir.replace('.vm', '.asm')
    else:
        return glob.glob(file_or_dir+'/*.vm'), file_or_dir+'/'+file_or_dir+'.asm'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print( "Modo de uso: VMtraductor [archivo.vm|directorio]" )
    else:
        archivosEntrada, archivoSalida = get_files( sys.argv[1] )
        trans = VMTraductor()
        print(f'archivo entrada: {archivosEntrada[0]}')
        print(f'archivo salida: {archivoSalida}')
        trans.traducir_VM(archivosEntrada, archivoSalida)


#main()