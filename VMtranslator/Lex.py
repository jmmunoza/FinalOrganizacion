
import re  #uso de expresiones regulares

NUM     = 1     # numero 
ID      = 2     # simbolo "palabra reservada"
ERROR   = 3     # error en la interpretación


class Lex(object):            
    def __init__(self, nombre_archivo):
        file = open(nombre_archivo, 'r')
        self._lineas = file.read()
        self._tokens = self._tokenize(self._lineas.split('\n'))
        self.comando_actual = []         # lista de tokens para el comando actual
        self.token_actual = (ERROR, 0)   # token actual del comando actual

    
    def __str__(self):
        pass

    def has_more_commands(self):
        return self._tokens != []
        
    def next_command(self):
        self.comando_actual = self._tokens.pop(0)
        self.next_token()
        return self.comando_actual
        
    def has_next_token(self):
        return self.comando_actual != []
        
    def next_token(self):
        if self.has_next_token():
            self.token_actual = self.comando_actual.pop(0)
        else:
            self.token_actual = (ERROR, 0)
        return self.token_actual
        
    def peek_token(self):
        if self.has_next_token():
            return self.comando_actual[0]
        else:
            return (ERROR, 0)
        
    def _tokenize(self, lineas):
        return [t for t in [self._tokenize_line(l) for l in lineas] if t!=[]]
    
    def _tokenize_line(self, linea):
        return [self._token(palabra) for palabra in self._split(self._remove_comentario(linea))]
	
    _comentario = re.compile('//.*$')
    def _remove_comentario(self, linea):
        return self._comentario.sub('', linea)

    _num_re = r'\d+'
    _id_re = r'[\w\-.]+'
    _palabra = re.compile(_num_re+'|'+_id_re)
    def _split(self, linea):
        return self._palabra.findall(linea)
		
    def _token(self, palabra):
        if   self._is_num(palabra):     return (NUM, palabra)
        elif self._is_id(palabra):      return (ID, palabra)
        else:                        return (ERROR, palabra)
			
    def _is_num(self, palabra):
        return self._is_match(self._num_re, palabra)
        
    def _is_id(self, palabra):
        return self._is_match(self._id_re, palabra)
        
    def _is_match(self, re_str, palabra):
        return re.match(re_str, palabra) != None