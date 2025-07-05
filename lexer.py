import ply.lex as lex

keywords = {
    'room': 'ROOM', 'item': 'ITEM', 'eco': 'ECO', 'objeto': 'OBJETO',
    'saida': 'SAIDA', 'desc': 'DESC', 'revela': 'REVELA', 'estado': 'ESTADO',
    'interacao': 'INTERACAO', 'quando': 'QUANDO', 'fazer': 'FAZER',
    'fimdejogo': 'FIMDEJOGO', 'print': 'PRINT', 'ganhar_item': 'GANHAR_ITEM',
    'perder_item': 'PERDER_ITEM', 'ganhar_eco': 'GANHAR_ECO',
    'remover_objeto': 'REMOVER_OBJETO', 'definir_estado': 'DEFINIR_ESTADO',
    'definir_saidas': 'DEFINIR_SAIDAS', 'teleportar': 'TELEPORTAR',
    'tem_item': 'TEM_ITEM', 'estado_sala_eh': 'ESTADO_SALA_EH',
    'sala_atual_eh': 'SALA_ATUAL_EH'
}

tokens = [
    'ID', 'STRING', 'LBRACE', 'RBRACE', 'EQUALS'
] + list(keywords.values())

t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_EQUALS = r'='
t_ignore = ' \t'
t_ignore_COMMENT = r'//.*'

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = keywords.get(t.value.lower(), 'ID')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()