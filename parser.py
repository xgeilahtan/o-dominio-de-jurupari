# parser.py
import ply.yacc as yacc
from lexer import tokens, lexer # Importamos o lexer também para o teste

# Dicionário para armazenar o mundo do jogo
game_world = {
    'rooms': {},
    'items': {},
    'commands': {}
}

# --- GRAMÁTICA ---

def p_game_spec(p):
    'game_spec : statement_list'
    p[0] = game_world

def p_statement_list_single(p):
    'statement_list : statement'
    pass

def p_statement_list_multiple(p):
    'statement_list : statement_list statement'
    pass

def p_statement(p):
    '''statement : room_def
                 | connect_def
                 | item_def
                 | command_def'''
    pass

def p_room_def(p):
    'room_def : ROOM ID STRING'
    room_name = p[2]
    description = p[3]
    game_world['rooms'][room_name] = {
        'description': description,
        'connections': {},
        'items': []
    }
    print(f"Parser: Sala '{room_name}' criada.")

def p_connect_def(p):
    'connect_def : CONNECT ID DIRECTION ID'
    source_room = p[2]
    direction = p[3]
    dest_room = p[4]
    if source_room in game_world['rooms']:
        game_world['rooms'][source_room]['connections'][direction] = dest_room
        print(f"Parser: Conexão de '{source_room}' --{direction}--> '{dest_room}' criada.")
    else:
        print(f"Erro: Sala '{source_room}' não encontrada para criar conexão.")

def p_item_def(p):
    'item_def : ITEM ID STRING IN ID'
    item_name = p[2]
    description = p[3]
    room_name = p[5]
    if room_name in game_world['rooms']:
        game_world['items'][item_name] = {'description': description, 'location': room_name}
        game_world['rooms'][room_name]['items'].append(item_name)
        print(f"Parser: Item '{item_name}' criado em '{room_name}'.")
    else:
        print(f"Erro: Sala '{room_name}' não encontrada para adicionar item.")

def p_error(p):
    if p:
        print(f"Erro de sintaxe no token '{p.type}' ('{p.value}') na linha {p.lineno}")
    else:
        print("Erro de sintaxe no fim do arquivo!")

# Adicione esta nova função ao parser.py
def p_command_def(p):
    'command_def : COMMAND ID ID COLON WHEN condition DO action_list'
    verb = p[2]
    target = p[3]
    condition_data = p[6]
    action_data = p[8]

    # Armazenamos o comando de forma estruturada
    command_key = f"{verb}_{target}"
    game_world['commands'][command_key] = {
        'verb': verb,
        'target': target,
        'condition': condition_data,
        'actions': action_data
    }
    print(f"Parser: Comando '{command_key}' criado.")

# Adicione estas novas funções ao parser.py
def p_condition(p):
    '''condition : ID IN ITEMS
                 | ROOM IS STRING'''
    if p[2] == 'in':
        # Guarda a condição como uma tupla: ('in_inventory', 'nome_do_item')
        p[0] = ('in_inventory', p[1]) 
    elif p[2] == 'is':
        # Guarda a condição como uma tupla: ('is_in_room', 'nome_da_sala')
        p[0] = ('is_in_room', p[3])

# Adicione estas novas funções ao parser.py
def p_action_list_single(p):
    'action_list : action'
    p[0] = [ p[1] ] # Retorna uma lista contendo uma única ação

def p_action_list_multiple(p):
    'action_list : action_list AND action'
    p[1].append(p[3]) # Adiciona a nova ação à lista existente
    p[0] = p[1]

def p_action(p):
    '''action : PRINT STRING
              | GET ID
              | RELEASE ID'''
    # Guarda a ação como uma tupla: ('verbo', 'argumento')
    p[0] = (p[1], p[2])



# Construir o parser
parser = yacc.yacc()

# --- Rotina de Teste ---
if __name__ == "__main__":
    try:
        with open('jogo_completo.txt', 'r', encoding='utf-8') as f:
            data = f.read()
    except FileNotFoundError:
        print("Erro: Arquivo 'jogo_completo.txt' não encontrado.")
        data = ''

    # Faz o parsing da entrada
    result = parser.parse(data, lexer=lexer)
    
    # Imprime o resultado final para verificação
    import json
    print("\n--- ESTRUTURA DO MUNDO DO JOGO CRIADA ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("--- FIM DO PARSING ---")