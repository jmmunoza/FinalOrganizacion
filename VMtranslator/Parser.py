
import Lex
from VMConstantes import *

class Parser(object):
    # Tipos de comando según guia
    _tipo_comando = {'add':C_ARITHMETIC, 'sub':C_ARITHMETIC, 'neg':C_ARITHMETIC,
                    'eq' :C_ARITHMETIC, 'gt' :C_ARITHMETIC, 'lt' :C_ARITHMETIC,
                    'and':C_ARITHMETIC, 'or' :C_ARITHMETIC, 'not':C_ARITHMETIC,
                    'label':C_LABEL,    'goto':C_GOTO,      'if-goto':C_IF, 
                    'push':C_PUSH,      'pop':C_POP, 
                    'call':C_CALL,      'return':C_RETURN,  'function':C_FUNCTION}

    # comandos con argumentos.
    _sin_argumentos = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not', 'return']
    _uniarios = ['label', 'goto', 'if-goto']
    _binarios = ['push', 'pop', 'function', 'call']
    
    def __init__(self, file):
        self.lex = Lex.Lex(file)
        self._init_comando_informacion()
    
    def _init_comando_informacion(self):
        self._cmd_type = C_ERROR
        self._arg1 = ''
        self._arg2 = 0
        
    def __str__(self):
        pass
        
    def has_more_commands(self):
        return self.lex.has_more_commands()
    
    # Lee comando por linea del archivo
    def advance(self):
        self._init_comando_informacion()

        self.lex.next_command()
        tok, val = self.lex.token_actual
        
        if tok != Lex.ID:
            pass                                # error
        if val in self._sin_argumentos:
            self._sin_argumentos_command(val)
        elif val in self._uniarios:
            self._uniarios_command(val)
        elif val in self._binarios:
            self._binarios_command(val)

    def command_type(self):
        return self._cmd_type 
        
    def arg1(self):
        return self._arg1
    
    def arg2(self):
        return self._arg2

    # Parser para cada tipo de comandos
    def _leer_tipo_comando(self, id):
        self._cmd_type = self._tipo_comando[id]
        
    def _sin_argumentos_command(self, id):
        self._leer_tipo_comando(id)
        if self._tipo_comando[id] == C_ARITHMETIC:
            self._arg1 = id

    def _uniarios_command(self, id):
        self._sin_argumentos_command(id)
        tok, val = self.lex.next_token()
        self._arg1 = val
        
    def _binarios_command(self, id):
        self._uniarios_command(id)
        tok, val = self.lex.next_token()
        self._arg2 = int(val)