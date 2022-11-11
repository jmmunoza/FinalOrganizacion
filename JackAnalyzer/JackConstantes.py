
# Gramatica JACK

# Tiposa de Tokens
T_KEYWORD       = 0     # No Terminales 'class', 'false' etc
T_SYM           = 1     # simbolos '{', '}' etc
T_NUM           = 2     # numeros '123' - desde el 0 al 32767
T_STR           = 3     # textos "Hola mundo"
T_ID            = 4     # identificadores 'nombre', 'id_42'
T_ERROR         = 5     # errores

# No Terminales
KW_CLASS        = 'class'
KW_METHOD       = 'method'
KW_FUNCTION     = 'function'
KW_CONSTRUCTOR  = 'constructor'
KW_INT          = 'int'
KW_BOOLEAN      = 'boolean'
KW_CHAR         = 'char'
KW_VOID         = 'void'
KW_VAR          = 'var'
KW_STATIC       = 'static'
KW_FIELD        = 'field'
KW_LET          = 'let'
KW_DO           = 'do'
KW_IF           = 'if'
KW_ELSE         = 'else'
KW_ELIF         = 'elif'
KW_WHILE        = 'while'
KW_RETURN       = 'return'
KW_TRUE         = 'true'
KW_FALSE        = 'false'
KW_NULL         = 'null'
KW_THIS         = 'this'
KW_NONE         = ''
KW_LONG         = 'long'
KW_STRING       = 'string'
KW_FOR          = 'for'
KW_FOREACH      = 'foreach'
KW_CONTINUE     = 'continue'
KW_BREAK        = 'break'
KW_SWITCH       = 'switch'
KW_CASE         = 'case'
KW_DEFAULT      = 'default'
KW_LIST         = 'list'

keywords = [KW_CLASS,  KW_METHOD,  KW_FUNCTION, KW_CONSTRUCTOR, KW_INT,    KW_BOOLEAN,
            KW_CHAR,   KW_VOID,    KW_VAR,      KW_STATIC,      KW_FIELD,  KW_LET,     KW_DO,      KW_IF,
            KW_ELSE,   KW_WHILE,   KW_RETURN,   KW_TRUE,        KW_FALSE,  KW_NULL,    KW_THIS,    KW_LONG,
            KW_STRING, KW_FOREACH, KW_CONTINUE, KW_BREAK,       KW_SWITCH, KW_CASE,    KW_DEFAULT, KW_ELIF,
            KW_FOR,    KW_LIST]

# Tokens
tokens = ['keyword', 'symbol', 'integerConstant', 'stringConstant', 'identifier']

# Simbolos
symbols = [':', '{', '}', '(', ')', '[', ']', '.', ';', ',', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']