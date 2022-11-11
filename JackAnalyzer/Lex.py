
import re, os
from xml.sax.saxutils import escape
from JackConstantes import *

# Analiza el código fuente 

class Lex(object):
    def __init__(self, archivo):
        arcchivo_entrada = open(archivo, 'r')
        self._lines = arcchivo_entrada.read()
        self._tokens = self._tokenize(self._lines)
        self._tipo_token = T_ERROR              # Tipo del token actual
        self._valor_token_actual = 0            # Valor del token actual
    
    def __str__(self):
        pass

    def openout(self, archivo):
        self._archivo_salida = open(archivo.replace('.jack', '_tokens.xml'), 'w')
        self._archivo_salida.write('<tokens>\n')

    def closeout(self):
        self._archivo_salida.write('</tokens>')
        self._archivo_salida.close()
        
    def has_more_tokens(self):
        return self._tokens != []
        
    def advance(self):
        if self.has_more_tokens():
            self._tipo_token, self._valor_token_actual = self._tokens.pop(0)
        else:
            self._tipo_token, self._valor_token_actual = (T_ERROR, 0)
        self._writexml()
        return (self._tipo_token, self._valor_token_actual)
        
    def peek(self):
        if self.has_more_tokens():
            return self._tokens[0]
        else:
            return (T_ERROR, 0)

    def _writexml(self):
        tok, val = self._tipo_token, self._valor_token_actual
        self._write_start_tag(tokens[tok])
        if   tok == T_KEYWORD:  
            self._archivo_salida.write(self.keyword())
        elif tok == T_SYM:      
            self._archivo_salida.write(escape(self.symbol()))
        elif tok == T_NUM:      
            self._archivo_salida.write(self.int_val())
        elif tok == T_STR:      
            self._archivo_salida.write(self.string_val())
        elif tok == T_ID:       
            self._archivo_salida.write(self.identifier())
        elif tok == T_ERROR:    
            self._archivo_salida.write('<<ERROR>>')
        self._write_end_tag(tokens[tok])
        
    def _write_start_tag(self, token):
        self._archivo_salida.write('<'+token+'> ')
    
    def _write_end_tag(self, token):
        self._archivo_salida.write(' </'+token+'>\n')
        
    def token_type(self):
        return self._tipo_token
        
    def keyword(self):
        return self._valor_token_actual
        
    def symbol(self):
        return self._valor_token_actual
        
    def identifier(self):
        return self._valor_token_actual
        
    def int_val(self):
        return self._valor_token_actual
        
    def string_val(self):
        return self._valor_token_actual
                
    def _tokenize(self, lines):
        return [self._token(word) for word in self._split(self._remove_comments(lines))]
	
    _comentario_re = re.compile(r'//[^\n]*\n|/\*(.*?)\*/', re.MULTILINE|re.DOTALL)
    def _remove_comments(self, line):
        return self._comentario_re.sub('', line)

    _keyword_re = '|'.join(keywords)

    # Sym_re new form
    _sym_re = '['
    for sym in symbols: _sym_re += re.escape(sym) + '|'
    _sym_re = _sym_re[:-1] + ']'  

    _num_re = r'\d+'
    _str_re = r'"[^"\n]*"'
    _id_re = r'[^\W0-9]\w*'
    
    _word = re.compile(_keyword_re+'|'+_sym_re+'|'+_num_re+'|'+_str_re+'|'+_id_re)

    def _split(self, line):
        return self._word.findall(line)

    def _token(self, word):
        
        if   self._is_keyword(word):    
            return (T_KEYWORD, word)
        elif self._is_sym(word):        
            return (T_SYM, word)
        elif self._is_num(word):        
            return (T_NUM, word)
        elif self._is_str(word):        
            return (T_STR, word[1:-2])
        elif self._is_id(word):        
            return (T_ID, word)
        else:                           
            return (T_ERROR, word)

    def _is_keyword(self, word):
        return self._is_match(self._keyword_re, word)
        
    def _is_sym(self, word):
        return self._is_match(self._sym_re, word)
        
    def _is_num(self, word):
        return self._is_match(self._num_re, word)
        
    def _is_str(self, word):
        return self._is_match(self._str_re, word)
        
    def _is_id(self, word):
        return self._is_match(self._id_re, word)
        
    def _is_match(self, re_str, word):
        return re.match(re_str, word) != None