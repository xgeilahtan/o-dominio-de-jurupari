# jogo.py
import parser as game_parser # Seu arquivo do parser é importado aqui
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
        # O parser transforma o texto do arquivo na estrutura de dados do nosso mundo
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
    # Imprime o nome da sala de forma amigável
    print(f"\n--- {current_room_name.replace('_', ' ').title()} ---")
    print(room_data['description'])

    # Mostra os itens na sala com nomes amigáveis
    if room_data['items']:
        print("\nVocê vê aqui:")
        for item_key in room_data['items']:
            print(f"- {item_key.replace('_', ' ')}")

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
    
    # <-- CORREÇÃO 1: Lidar com alvos de múltiplas palavras.
    # Junta todas as palavras após o verbo para formar o nome completo do alvo.
    alvo_nome_amigavel = " ".join(partes[1:]) if len(partes) > 1 else None
    # Cria uma versão do nome para usar como chave (com underscores), que é como o parser salva.
    alvo_chave = alvo_nome_amigavel.replace(' ', '_') if alvo_nome_amigavel else None

    current_room_name = player_state['current_room']
    room_data = game_world['rooms'][current_room_name]

    if verbo == 'ir' and alvo_nome_amigavel in room_data['connections']:
        player_state['current_room'] = room_data['connections'][alvo_nome_amigavel]
        
    elif verbo == 'pegar' and alvo_chave in room_data['items']:
        # <-- CORREÇÃO 2: Usar a 'alvo_chave' para encontrar o item.
        room_data['items'].remove(alvo_chave)
        player_state['inventory'].append(alvo_chave)
        print(f"Você pegou: {alvo_nome_amigavel}") # Mostra o nome bonito para o jogador
        
    elif verbo == 'inventario':
        if player_state['inventory']:
            print("Seu inventário:")
            # Mostra os nomes dos itens de forma amigável
            for item_key in player_state['inventory']:
                print(f"- {item_key.replace('_', ' ')}")
        else:
            print("Seu inventário: vazio")
            
    elif verbo == 'usar' and alvo_chave:
        # <-- CORREÇÃO 3: Construir a chave do comando usando a 'alvo_chave'.
        # Isso garante que "usar_amuleto_de_palha" vai corresponder ao que o parser criou.
        command_key = f"usar_{alvo_chave}"
        
        if command_key in game_world['commands']:
            command_data = game_world['commands'][command_key]
            condicao = command_data['condition']
            condicao_atendida = False
            
            # Verifica a condição do comando
            if condicao[0] == 'in_inventory' and condicao[1] in player_state['inventory']:
                condicao_atendida = True
            # (No futuro, você poderia adicionar mais tipos de condições aqui, como 'is_in_room')
            
            if condicao_atendida:
                # Executa as ações se a condição for atendida
                for acao in command_data['actions']:
                    if acao[0] == 'print':
                        print(acao[1])
            else:
                print("Nada acontece.")
        else:
            print(f"Você não pode usar '{alvo_nome_amigavel}' dessa forma ou aqui.")
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
        
        try:
            comando = input("\n> ").strip()
        except EOFError:
            print("\nAté a próxima...")
            break

        if not comando:
            continue
            
        if comando.lower() == 'sair':
            print("Até a próxima...")
            break
        
        processar_comando(comando, game_world, player_state)

if __name__ == "__main__":
    main()