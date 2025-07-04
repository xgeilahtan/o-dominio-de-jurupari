# parser.py
import ply.yacc as yacc
from lexer import lexer, tokens # Importa o lexer diretamente

# --- GRAMÁTICA (cria uma lista de definições - AST) ---

def p_program(p):
    'program : statement_list'
    p[0] = p[1]

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | empty'''
    if len(p) > 2 and p[2]:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2:
        p[0] = [p[1]] if p[1] else []
    else:
        p[0] = []

def p_statement(p):
    '''statement : item_def
                 | eco_def
                 | room_def
                 | interaction_def'''
    p[0] = p[1]

def p_item_def(p):
    'item_def : ITEM ID STRING LBRACE DESC STRING RBRACE'
    p[0] = ('item', {'id': p[2], 'nome': p[3], 'descricao': p[6]})

def p_eco_def(p):
    'eco_def : ECO ID STRING LBRACE DESC STRING RBRACE'
    p[0] = ('eco', {'id': p[2], 'titulo': p[3], 'descricao': p[6]})

def p_room_def(p):
    'room_def : ROOM ID STRING LBRACE statement_list RBRACE'
    p[0] = ('room', {'id': p[2], 'nome': p[3], 'statements': p[5]})

def p_interaction_def(p):
    'interaction_def : INTERACAO ID ID LBRACE statement_list RBRACE'
    p[0] = ('interacao', {'verbo': p[2], 'alvo': p[3], 'statements': p[5]})

def p_inline_statement(p):
    '''statement : DESC STRING
                 | SAIDA ID ID
                 | OBJETO ID STRING
                 | OBJETO ID STRING LBRACE REVELA ID RBRACE
                 | ESTADO ID EQUALS ID
                 | QUANDO LBRACE statement_list RBRACE
                 | FAZER LBRACE statement_list RBRACE
                 | SALA_ATUAL_EH ID
                 | TEM_ITEM ID
                 | ESTADO_SALA_EH ID EQUALS ID
                 | PRINT STRING
                 | GANHAR_ITEM ID
                 | PERDER_ITEM ID
                 | GANHAR_ECO ID
                 | REMOVER_OBJETO ID
                 | DEFINIR_ESTADO ID EQUALS ID
                 | DEFINIR_SAIDAS LBRACE statement_list RBRACE
                 | FIMDEJOGO STRING
                 | TELEPORTAR ID'''
    tipo = p[1].upper()
    if tipo in ('ESTADO', 'DEFINIR_ESTADO', 'ESTADO_SALA_EH'): p[0] = (tipo, p[2], p[4])
    elif tipo in ('QUANDO', 'FAZER', 'DEFINIR_SAIDAS'): p[0] = (tipo, p[3])
    elif tipo == 'OBJETO' and len(p) > 4: p[0] = (tipo, p[2], p[3], {'revela': p[6]})
    elif len(p) == 2: p[0] = (tipo,)
    elif len(p) == 3: p[0] = (tipo, p[2])
    elif len(p) == 4: p[0] = (tipo, p[2], p[3])

def p_empty(p): 'empty :'
pass

def p_error(p):
    if p: print(f"Erro de Sintaxe no token '{p.type}' com valor '{p.value}' na linha {p.lineno}")
    else: print("Erro de Sintaxe no final do arquivo!")

parser = yacc.yacc(debug=False)

# --- FUNÇÃO DE INTERFACE DO PARSER (A PARTE QUE FALTAVA) ---
# Adicione esta função no final do seu arquivo parser.py

def get_ast(data):
    """
    Função principal para chamar o parser. Ela reseta o estado do lexer
    e do parser para garantir que uma nova análise seja limpa.
    """
    # Reinicia o estado do lexer para o início do texto
    lexer.lineno = 1
    # Chama o parser
    result = parser.parse(data, lexer=lexer)
    return result