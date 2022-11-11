import sys, os, os.path, glob
import Parser

class JackAnalyzer(object):
    def __init__(self):
        pass

    def analyze(self, archivo_entrada, archivo_salida):
        for infile in archivo_entrada:
            Parser.Parser(infile)

def get_files( file_or_dir ):
    if file_or_dir.endswith('.jack'):
        return [file_or_dir], file_or_dir.replace('.jack', '.xml')
    else:
        return glob.glob(file_or_dir+'/*.jack'), file_or_dir+'/'+file_or_dir+'.xml'


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print( "Modo de uso: py AnalizadorJack.py [archivo.jack|dir]" )
    else:
        archivo_entrada, archivo_salida = get_files( sys.argv[1] )
        print('-'*45)
        print('PROGRAMA COMPILADOR DE LENGUAJE DE ALTO NIVEL')
        print('-'*45)
        print(f'archivo de salida: {archivo_salida}')
        print(f'archivos de entrada:: Cantidad:{len(archivo_entrada)}  fuentes:{archivo_entrada}')
        analizador = JackAnalyzer()
        analizador.analyze(archivo_entrada, archivo_salida)
        print('-'*45)
