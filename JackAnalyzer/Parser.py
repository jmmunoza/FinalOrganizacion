
import Lex, os, os.path
from xml.sax.saxutils import escape
from JackConstantes import *

# Parses Jack

class ParserError(Exception):
    def __init__(self, mensaje):
        self.message = mensaje
    
class Parser(object):
    def __init__(self, archivo):
        self.lex = Lex.Lex(archivo)
        self.openout(archivo)
        self.compile_class()
        self.closeout()
        
    def __str__(self):
        pass
        
    # Procesos de avance en el documento fuente
    def _require(self, tok, val=None):
        lextok, lexval = self._advance()
        if tok != lextok or ((tok == T_KEYWORD or tok == T_SYM) and val != lexval):
            raise ParserError(self._require_failed_msg(tok, val))
        else:
            return lexval
            
    def _require_failed_msg(self, tok, val):
        if val == None: val = tok
        return 'Token esperado: '+val
    
    def _advance(self):
        tok, val = self.lex.advance()
        self._write_terminal(tok, val)
        return tok, val

    def _is_token(self, tok, val=None):
        lextok, lexval = self.lex.peek()
        if val == None:
            return lextok == tok
        else:
            return (lextok, lexval) == (tok, val)
        
    # escritura del archivo XML        
    def openout(self, path):
        outdir = os.path.join(os.path.dirname(path), 'output')
        archivo = os.path.join(outdir, os.path.basename(path))
        try:
            os.mkdir(outdir)
        except OSError as e:
            pass
        self._archivo_salida = open(archivo.replace('.jack', '.xml'), 'w')
        self.lex.openout(archivo)
    
    def closeout(self):
        self.lex.closeout()
        self._archivo_salida.close()

    def _write_terminal(self, tok, val):
        self._archivo_salida.write('<'+tokens[tok]+'> '+escape(val)+' </'+tokens[tok]+'>\n')
        
    _parsed_rules = []
    def _start_non_terminal(self, rule):
        self._archivo_salida.write('<'+rule+'>\n')
        self._parsed_rules = [rule] + self._parsed_rules
        
    def _end_non_terminal(self):
        rule = self._parsed_rules.pop(0)
        self._archivo_salida.write('</'+rule+'>\n')

    # Parser and compilador del codigo fuente Jack        
    def compile_class(self):
        self._start_non_terminal('class')
        self._require(T_KEYWORD, KW_CLASS)
        class_name = self._require(T_ID)
        self._require(T_SYM, '{')

        while self._is_class_var_dec():
            self.compile_class_var_dec()

        while self._is_subroutine():
            self.compile_subroutine()

        self._require(T_SYM, '}')
        self._end_non_terminal()
        
    # Declaraci??n de variables
    def _is_class_var_dec(self):
        return self._is_token(T_KEYWORD, KW_STATIC) or self._is_token(T_KEYWORD, KW_FIELD)
            
    def compile_class_var_dec(self):
        self._start_non_terminal('classVarDec')
        tok, kwd = self._advance()                  # static | field
        self._compile_dec()
        self._end_non_terminal()
        
    def _compile_dec(self):
        self.compile_type()
        self.compile_var_name()
        while self._is_token(T_SYM, ','):
            self._require(T_SYM, ',')
            self.compile_var_name()
        self._require(T_SYM, ';')
    
    def _is_type(self):
        tok, val = self.lex.peek()
        return tok == T_KEYWORD and (val == KW_INT or val == KW_CHAR or val == KW_BOOLEAN or val == KW_LONG or val == KW_STRING or val == KW_LIST) or tok == T_ID

    def compile_type(self):
        if self._is_type():
            return self._advance()
        else:
            raise ParserError(self._require_failed_msg(*self.lex.peek()))
        
    def compile_void_or_type(self):
        if self._is_token(T_KEYWORD, KW_VOID):
            return self._advance()
        else:
            self.compile_type()
            
    def _is_var_name(self):
        return self._is_token(T_ID)
        
    def compile_var_name(self):
        self._require(T_ID)
        
    # Declaraci??n de subrutinas
    def _is_subroutine(self):
        tok, kwd = self.lex.peek()
        return tok == T_KEYWORD and (kwd == KW_CONSTRUCTOR or kwd == KW_FUNCTION or kwd == KW_METHOD)
        
    def compile_subroutine(self):
        self._start_non_terminal('subroutineDec')
        kwd = self._advance()
        self.compile_void_or_type()
        self.compile_var_name()
        self._require(T_SYM, '(')
        self.compile_parameter_list()
        self._require(T_SYM, ')')
        self.compile_subroutine_body()
        self._end_non_terminal()
                
    def compile_parameter_list(self):
        self._start_non_terminal('parameterList')
        self.compile_parameter()
        while self._is_token(T_SYM, ','):
            self._advance()
            self.compile_parameter()
        self._end_non_terminal()
              
    def compile_parameter(self):
        if self._is_type():
            self.compile_type()
            self.compile_var_name()
            
    def compile_subroutine_body(self):
        self._start_non_terminal('subroutineBody')
        self._require(T_SYM, '{')
        while self._is_var_dec():
            self.compile_var_dec()
        self.compile_statements()
        self._require(T_SYM, '}')
        self._end_non_terminal()
        
    def _is_var_dec(self):
        return self._is_token(T_KEYWORD, KW_VAR)
        
    def compile_var_dec(self):
        self._start_non_terminal('varDec')
        self._require(T_KEYWORD, KW_VAR)
        self._compile_dec()
        self._end_non_terminal()
        
    # declaraciones
    def compile_statements(self):
        self._start_non_terminal('statements')
        while self._is_statement():
            self._compile_statement()
        self._end_non_terminal()
    
    def _is_statement(self):
        return self._is_foreach() or self._is_continue() or self._is_break() or self._is_switch() or self._is_do() or self._is_let() or self._is_if() or self._is_while() or self._is_return() or self._is_for()
        
    def _compile_statement(self):
        if   self._is_do():     
            self.compile_do()
        elif self._is_let():    
            self.compile_let()
        elif self._is_if():     
            self.compile_if()
        elif self._is_while():  
            self.compile_while()
        elif self._is_return(): 
            self.compile_return()
        elif self._is_for():
            self.compile_for()
        elif self._is_foreach():
            self.compile_foreach()
        elif self._is_switch():
            self.compile_switch()
        elif self._is_continue():
            self.compile_continue()
        elif self._is_break():
            self.compile_break()

    def _is_switch(self):
        return self._is_token(T_KEYWORD, KW_SWITCH)

    def compile_switch(self):
        self._start_non_terminal('switchStatement')
        self._require(T_KEYWORD, KW_SWITCH)
        self._require(T_SYM, '(')
        self.compile_expression()
        self._require(T_SYM, ')')
        self._require(T_SYM, '{')

        while self._is_token(T_KEYWORD, KW_CASE):
            self._require(T_KEYWORD, KW_CASE)
            self.compile_expression()
            self._require(T_SYM, ':')
            self.compile_statements()
            
        if self._is_token(T_KEYWORD, KW_DEFAULT):
            self._require(T_KEYWORD, KW_DEFAULT)
            self._require(T_SYM, ':')
            self.compile_statements()

        self._require(T_SYM, '}')
        self._end_non_terminal()

    def _is_do(self):
        return self._is_token(T_KEYWORD, KW_DO)
        
    def compile_do(self):
        self._start_non_terminal('doStatement')
        self._require(T_KEYWORD, KW_DO)
        self._require(T_ID)
        self.compile_subroutine_call()
        self._require(T_SYM, ';')
        self._end_non_terminal()
        
    def _is_let(self):
        return self._is_token(T_KEYWORD, KW_LET)
        
    def compile_let(self):
        self._start_non_terminal('letStatement')
        self._require(T_KEYWORD, KW_LET)
        self.compile_var_name()
        if self._is_token(T_SYM, '['):
            self._advance()
            self.compile_expression()
            self._require(T_SYM, ']')
        
        if self._is_token(T_SYM, '+'):
            self._advance()
            if self._is_token(T_SYM, '+'):
                self._advance()
            else:
                self._require(T_SYM, '=')
                self.compile_expression()

        elif self._is_token(T_SYM, '-'):
            self._advance()
            if self._is_token(T_SYM, '-'):
                self._advance()
            else:
                self._require(T_SYM, '=')
                self.compile_expression()

        elif self._is_token(T_SYM, '*') or self._is_token(T_SYM, '/'):
            self._advance()
            self._require(T_SYM, '=')
            self.compile_expression()
        else:
            self._require(T_SYM, '=')
            
            if self._is_token(T_SYM, '['):
                self._require(T_SYM, '[')
                self.compile_expression_list()
                self._require(T_SYM, ']')
            else:
                self.compile_expression()

        self._require(T_SYM, ';')
        self._end_non_terminal()
        
    def _is_while(self):
        return self._is_token(T_KEYWORD, KW_WHILE)
        
    def compile_while(self):
        self._start_non_terminal('whileStatement')
        self._require(T_KEYWORD, KW_WHILE)
        self._compile_cond_expression_statements()
        self._end_non_terminal()

    def _is_continue(self):
        return self._is_token(T_KEYWORD, KW_CONTINUE)
        
    def compile_continue(self):
        self._start_non_terminal('continueStatement')
        self._require(T_KEYWORD, KW_CONTINUE)
        self._require(T_SYM, ';')
        self._end_non_terminal()
        
    def _is_break(self):
        return self._is_token(T_KEYWORD, KW_BREAK)
        
    def compile_break(self):
        self._start_non_terminal('breakStatement')
        self._require(T_KEYWORD, KW_BREAK)
        self._require(T_SYM, ';')
        self._end_non_terminal()

    def _is_return(self):
        return self._is_token(T_KEYWORD, KW_RETURN)
        
    def compile_return(self):
        self._start_non_terminal('returnStatement')
        self._require(T_KEYWORD, KW_RETURN)
        if not self._is_token(T_SYM, ';'):
            self.compile_expression()
        self._require(T_SYM, ';')
        self._end_non_terminal()
        
    def _is_if(self):
        return self._is_token(T_KEYWORD, KW_IF)
        
    def compile_if(self):
        self._start_non_terminal('ifStatement')
        self._require(T_KEYWORD, KW_IF)
        self._compile_cond_expression_statements()

        while self._is_token(T_KEYWORD, KW_ELIF):
            self._require(T_KEYWORD, KW_ELIF)
            self._compile_cond_expression_statements()

        if self._is_token(T_KEYWORD, KW_ELSE):
            self._require(T_KEYWORD, KW_ELSE)
            self._require(T_SYM, '{')
            self.compile_statements()
            self._require(T_SYM, '}')
        self._end_non_terminal()
        
    def _is_for(self):
        return self._is_token(T_KEYWORD, KW_FOR)
    
    def compile_for(self):
        self._start_non_terminal('forStatement')
        self._require(T_KEYWORD, KW_FOR)
        self._require(T_SYM, '(')
        self._require(T_SYM, ')')
        self._end_non_terminal()

    def _is_foreach(self):
        return self._is_token(T_KEYWORD, KW_FOREACH)
    
    def compile_foreach(self):
        self._start_non_terminal('foreachStatement')
        self._require(T_KEYWORD, KW_FOREACH)
        self._require(T_SYM, '(')
        self.compile_var_name()
        self._require(T_SYM, ':')
        self.compile_var_name()
        self._require(T_SYM, ')')
        self._require(T_SYM, '{')
        self.compile_statements()
        self._require(T_SYM, '}')
        self._end_non_terminal()

    def _compile_cond_expression_statements(self):
        self._require(T_SYM, '(')
        self.compile_expression()
        self._require(T_SYM, ')')
        self._require(T_SYM, '{')
        self.compile_statements()
        self._require(T_SYM, '}')

    # Expresiones
    def compile_expression(self):
        if not self._is_term():
            if self._is_token(T_SYM, ','):
                raise ParserError(self._require_failed_msg(*self.lex.peek()))
            return
            
        self._start_non_terminal('expression')
        self.compile_term()
        while self._is_op():
            self._advance()
            self.compile_term()
        self._end_non_terminal()
        
    def _is_term(self):
        return self._is_token(T_NUM) or self._is_token(T_STR) or self._is_keyword_constant()    \
            or self._is_var_name() or self._is_token(T_SYM, '(') or self._is_unary_op()
        
    def compile_term(self):
        self._start_non_terminal('term')
        if self._is_token(T_NUM) or self._is_token(T_STR) or self._is_keyword_constant():
            self._advance()
        elif self._is_token(T_SYM, '('):
            self._advance()
            self.compile_expression()
            self._require(T_SYM, ')')
        elif self._is_unary_op():
            self._advance()
            self.compile_term()
        elif self._is_var_name():
            self._advance()
            if self._is_token(T_SYM, '['):
                self._compile_array_subscript()
            elif self._is_token(T_SYM, '(') or self._is_token(T_SYM, '.'):
                self.compile_subroutine_call()
        self._end_non_terminal()

    def _compile_array_subscript(self):
        self._require(T_SYM, '[')
        self.compile_expression()
        self._require(T_SYM, ']')

    def compile_subroutine_call(self):  # first ID already advanced
        if self._is_token(T_SYM, '.'):
            self._advance()
            self._require(T_ID)
        self._require(T_SYM, '(')
        self.compile_expression_list()
        self._require(T_SYM, ')')
        
    def _is_keyword_constant(self):
        tok, kwd = self.lex.peek()
        return tok == T_KEYWORD and kwd in [KW_TRUE, KW_FALSE, KW_NULL, KW_THIS]

    def _is_unary_op(self):
        return self._is_token(T_SYM, '-') or self._is_token(T_SYM, '~')
        
    def _is_op(self):
        tok, sym = self.lex.peek()
        return tok == T_SYM and sym in '+-*/&|<>='
    
    def compile_expression_list(self):
        self._start_non_terminal('expressionList')
        self.compile_expression()

        while self._is_token(T_SYM, ','):
            self._require(T_SYM, ',')
            self.compile_expression()
        
        self._end_non_terminal()