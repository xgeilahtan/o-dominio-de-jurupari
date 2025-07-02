# jogo.py
import parser as game_parser
import json

# Estado inicial do jogador
player_state = {
    'current_room': 'cabana_velha',
    'inventory': []
}

def carregar_mundo(caminho_arquivo):
    """Lê um arquivo de jogo e usa nosso parser para construir o mundo."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            data = f.read()
        mundo = game_parser.parser.parse(data)
        return mundo
    except FileNotFoundError:
        print(f"Erro: Arquivo do mundo '{caminho_arquivo}' não encontrado.")
        return None

def exibir_status(game_world, player_state):
    """Mostra a descrição da sala atual, itens e saídas."""
    current_room_name = player_state['current_room']
    
    if current_room_name not in game_world['rooms']:
        print("Erro: Você está em uma sala desconhecida! Fim de jogo.")
        return False # Sinaliza para parar o jogo

    room_data = game_world['rooms'][current_room_name]
    print(f"\n--- {current_room_name.replace('_', ' ').title()} ---")
    print(room_data['description'])

    if room_data['items']:
        print("\nVocê vê aqui:")
        for item in room_data['items']:
            print(f"- {item}")

    if room_data['connections']:
        print("\nSaídas disponíveis:")
        for direction in room_data['connections']:
            print(f"- {direction}")
    return True

def processar_comando(comando_str, game_world, player_state):
    """Processa um comando digitado pelo jogador."""
    partes = comando_str.lower().split()
    if not partes:
        return

    verbo = partes[0]
    alvo = partes[1] if len(partes) > 1 else None
    
    current_room_name = player_state['current_room']
    room_data = game_world['rooms'][current_room_name]

    if verbo == 'ir' and alvo in room_data['connections']:
        player_state['current_room'] = room_data['connections'][alvo]
    elif verbo == 'pegar' and alvo in room_data['items']:
        room_data['items'].remove(alvo)
        player_state['inventory'].append(alvo)
        print(f"Você pegou: {alvo}")
    elif verbo == 'inventario':
        print("Seu inventário:", player_state['inventory'] if player_state['inventory'] else "vazio")
    elif verbo == 'usar' and alvo:
        command_key = f"usar_{alvo}"
        if command_key in game_world['commands']:
            command_data = game_world['commands'][command_key]
            condicao = command_data['condition']
            condicao_atendida = False
            if condicao[0] == 'in_inventory' and condicao[1] in player_state['inventory']:
                condicao_atendida = True
            
            if condicao_atendida:
                for acao in command_data['actions']:
                    if acao[0] == 'print':
                        print(acao[1])
            else:
                print("Nada acontece.")
        else:
            print("Você não pode usar isso dessa forma.")
    else:
        print("Comando inválido ou não entendi.")

def main():
    """Função principal que roda o jogo."""
    game_world = carregar_mundo('jogo_completo.txt')
    if not game_world:
        return

    print("--- O Domínio de Jurupari ---")
    print("Você acorda em uma cabana escura, sem saber como chegou aqui. Digite 'sair' para terminar.")

    while True:
        if not exibir_status(game_world, player_state):
            break
        
        comando = input("\n> ").lower()

        if comando == 'sair':
            print("Até a próxima...")
            break
        
        processar_comando(comando, game_world, player_state)

if __name__ == "__main__":
    main()