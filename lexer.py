# lexer.py
import ply.lex as lex

# --- ALTERAÇÃO 1: Dicionário de Palavras-Chave ---
# Todas as palavras reservadas da nossa linguagem
keywords = {
    'room':     'ROOM',
    'connect':  'CONNECT',
    'item':     'ITEM',
    'in':       'IN',
    'command':  'COMMAND',
    'when':     'WHEN',
    'do':       'DO',
    'and':      'AND',
    'or':       'OR',
    'not':      'NOT',
    'print':    'PRINT',
    'get':      'GET',
    'release':  'RELEASE',
    'is':       'IS',
    'items':    'ITEMS',
    # Adicionamos as direções aqui também para centralizar a lógica
    'north':    'DIRECTION',
    'south':    'DIRECTION',
    'east':     'DIRECTION',
    'west':     'DIRECTION'
}

# Lista de nomes dos tokens. Adicionamos as palavras-chave do dicionário.
tokens = [
    'ID',
    'STRING',
    'COLON',
] + list(set(keywords.values()))


# Regras complexas usando funções

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value[1:-1]  # Remove as aspas
    return t

# --- ALTERAÇÃO 2: Função t_ID atualizada ---
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    # Verifica se a palavra encontrada está no dicionário de keywords
    # Se estiver, muda o tipo do token. Se não, o tipo continua sendo 'ID'.
    t.type = keywords.get(t.value, 'ID')
    return t

# Regra para rastrear números de linha
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Ignorar espaços, tabs e comentários
t_ignore  = ' \t'
t_ignore_COMMENT = r'//.*'
t_COLON = r':'

# Tratamento de erro
def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

# Construir o lexer
lexer = lex.lex()

# --- Rotina de Teste (sem alterações) ---
if __name__ == "__main__":
    try:
        with open('jogo_exemplo.txt', 'r', encoding='utf-8') as f:
            data = f.read()
    except FileNotFoundError:
        print("Erro: Arquivo 'jogo_exemplo.txt' não encontrado.")
        data = ''

    lexer.input(data)

    print("--- INÍCIO DA ANÁLISE LÉXICA (VERSÃO CORRIGIDA) ---")
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)
    print("--- FIM DA ANÁLISE LÉXICA ---")