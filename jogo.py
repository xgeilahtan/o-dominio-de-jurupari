# jogo.py
# Versão final e completa, com compilador e motor de jogo interativo.

import parser as game_parser

# ==============================================================================
# SEÇÃO 1: DADOS GLOBAIS E ESTADO DO JOGADOR
# ==============================================================================

# Dicionários que serão preenchidos pelo compilador
MUNDO = {}
ITENS = {}
ECOS = {}
INTERACOES = []

# O estado do jogador, que muda durante o jogo
ESTADO_JOGADOR = {
    'localizacao_atual': 'cabana_velha',
    'inventario': [],
    'jogo_terminado': False,
    'estados_ativos': {'protegido_da_cancao': False},
    'ecos_coletados': []
}


# ==============================================================================
# SEÇÃO 2: COMPILADOR E CARREGADOR DO MUNDO
# ==============================================================================

def compilar_mundo(ast):
    """Processa a lista de definições do parser e constrói os dicionários do jogo."""
    for def_type, data in ast:
        if def_type == 'item': ITENS[data['id']] = data
        elif def_type == 'eco': ECOS[data['id']] = data
        elif def_type == 'room':
            room_data = {'nome': data['nome'], 'descricao': "", 'objetos': {}, 'itens': [], 'saidas': {}, 'estado': {}}
            for stmt in data.get('statements', []):
                stmt_type, *stmt_data = stmt
                if stmt_type == 'DESC': room_data['descricao'] = stmt_data[0]
                elif stmt_type == 'SAIDA': room_data['saidas'][stmt_data[0]] = stmt_data[1]
                elif stmt_type == 'OBJETO':
                    # Lógica corrigida para lidar com o bloco REVELA
                    obj_content = {'descricao': stmt_data[1]}
                    if len(stmt_data) > 2 and isinstance(stmt_data[2], dict):
                        obj_content.update(stmt_data[2])
                    room_data['objetos'][stmt_data[0]] = obj_content
                elif stmt_type == 'ESTADO': room_data['estado'][stmt_data[0]] = (stmt_data[1] == 'true')
            MUNDO[data['id']] = room_data
        elif def_type == 'interacao':
            interaction_data = {'verbo': data['verbo'], 'alvo': data['alvo'], 'condicoes': [], 'acoes': []}
            for stmt in data.get('statements', []):
                stmt_type, *stmt_data = stmt
                if stmt_type == 'QUANDO': interaction_data['condicoes'] = stmt_data[0]
                elif stmt_type == 'FAZER': interaction_data['acoes'] = stmt_data[0]
            INTERACOES.append(interaction_data)

def carregar_mundo(caminho_arquivo):
    """Lê o arquivo de jogo, chama o parser e compila o mundo."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        ast = game_parser.get_ast(conteudo)
        if ast: compilar_mundo(ast); return True
        else: print("ERRO: Parser não conseguiu analisar o arquivo do mundo. Verifique a sintaxe."); return False
    except FileNotFoundError:
        print(f"ERRO: Arquivo '{caminho_arquivo}' não encontrado."); return False

# ==============================================================================
# SEÇÃO 3: FUNÇÕES DO MOTOR DO JOGO
# ==============================================================================

def exibir_localizacao():
    """Mostra os detalhes da localização atual do jogador."""
    loc_id = ESTADO_JOGADOR['localizacao_atual']
    loc_data = MUNDO.get(loc_id, {})
    
    print(f"\n--- {loc_data.get('nome', 'Lugar Desconhecido')} ---")
    
    estado_sala = 'purificada' if loc_data.get('estado',{}).get('purificada') else 'amaldicoado'
    
    if loc_id == 'arvore_seca' and loc_data.get('estado',{}).get('purificada'):
        print(MUNDO['arvore_seca']['objetos'].get('arvore_purificada', {}).get('descricao', loc_data.get('descricao')))
    else:
        print(loc_data.get('descricao', "Não há nada aqui."))

    objetos_disponiveis = loc_data.get('objetos', {})
    if objetos_disponiveis:
        print("\nVocê também nota:", ", ".join(obj.replace('_', ' ').title() for obj in objetos_disponiveis.keys()))

    itens_na_sala = loc_data.get('itens', [])
    if itens_na_sala:
        print("\nVocê vê no chão:", ", ".join(ITENS.get(item, {}).get('nome', item) for item in itens_na_sala))
    
    saidas = loc_data.get('saidas', {})
    if saidas:
        print("\nSaídas disponíveis: " + ", ".join(saidas.keys()))

def processar_comando(comando, alvo):
    """Processa o comando do jogador, interpretando as regras de INTERACAO."""
    loc_id = ESTADO_JOGADOR['localizacao_atual']
    loc_data = MUNDO[loc_id]

    # --- 1. VERIFICAÇÃO DE PERIGOS AMBIENTAIS (Lógica da Iara Corrigida e Centralizada) ---
    if loc_id == 'lagoa' and not ESTADO_JOGADOR['estados_ativos']['protegido_da_cancao']:
        # Verifica se o jogador tem a cera para poder usar
        if comando == 'usar' and alvo == 'cera_de_ouvido' and 'cera_de_ouvido' in ESTADO_JOGADOR['inventario']:
            # Se usou a cera, toda a lógica acontece aqui e o turno acaba.
            ESTADO_JOGADOR['estados_ativos']['protegido_da_cancao'] = True
            print("Você rapidamente coloca a cera pegajosa nos ouvidos. O mundo fica abafado e distante. A canção da Iara, antes avassaladora, agora é apenas um murmúrio triste e inofensivo no fundo da sua mente. Você está seguro. No centro da lagoa, a melodia para. Uma figura emerge das águas e te encara.")
            return # AÇÃO EXECUTADA COM SUCESSO, FIM DO TURNO.
        else:
            # Se for qualquer outro comando, o jogo termina.
            print("A canção domina seus pensamentos. Esquecer... apagar a dor... A água parece quente e convidativa. Você dá um passo, depois outro, e a escuridão líquida te abraça, te puxando para o silêncio eterno do fundo. FIM DE JOGO.")
            ESTADO_JOGADOR['jogo_terminado'] = True
            return
        
    # 2. VERIFICAÇÃO DE INTERAÇÕES ESPECIAIS (Puzzles do .txt)
    for interacao in INTERACOES:
        cond_verbo = interacao['verbo'] == comando or interacao['verbo'] == 'qualquer'
        cond_alvo = interacao['alvo'] == alvo or interacao['alvo'] == 'qualquer' or (interacao['alvo'] == 'nenhum' and alvo is None)
        
        if cond_verbo and cond_alvo:
            condicoes_satisfeitas = True
            for tipo_cond, *valor_cond in interacao.get('condicoes', []):
                if tipo_cond == 'SALA_ATUAL_EH' and loc_id != valor_cond[0]: condicoes_satisfeitas = False; break
                if tipo_cond == 'TEM_ITEM' and valor_cond[0] not in ESTADO_JOGADOR['inventario']: condicoes_satisfeitas = False; break
                if tipo_cond == 'ESTADO_SALA_EH':
                    chave_estado, valor_esperado = valor_cond[0], (valor_cond[1] == 'true')
                    if loc_data.get('estado', {}).get(chave_estado) != valor_esperado: condicoes_satisfeitas = False; break
            
            if condicoes_satisfeitas:
                for tipo_acao, *valor_acao in interacao.get('acoes', []):
                    if tipo_acao == 'PRINT': print(valor_acao[0])
                    elif tipo_acao == 'FIMDEJOGO': print(valor_acao[0]); ESTADO_JOGADOR['jogo_terminado'] = True; return
                    elif tipo_acao == 'GANHAR_ITEM': ESTADO_JOGADOR['inventario'].append(valor_acao[0])
                    elif tipo_acao == 'PERDER_ITEM': 
                        if valor_acao[0] in ESTADO_JOGADOR['inventario']: ESTADO_JOGADOR['inventario'].remove(valor_acao[0])
                    elif tipo_acao == 'GANHAR_ECO':
                        if valor_acao[0] not in ESTADO_JOGADOR['ecos_coletados']:
                            ESTADO_JOGADOR['ecos_coletados'].append(valor_acao[0]); print(f"\nVocê sente um eco ({valor_acao[0]}) ressoar em sua alma.")
                    elif tipo_acao == 'REMOVER_OBJETO': 
                        if valor_acao[0] in loc_data['objetos']: del loc_data['objetos'][valor_acao[0]]
                    elif tipo_acao == 'DEFINIR_ESTADO': loc_data['estado'][valor_acao[0]] = (valor_acao[1] == 'true')
                    elif tipo_acao == 'DEFINIR_SAIDAS': 
                        novas_saidas = {}
                        for saida_stmt in valor_acao[0]: _, direcao, destino = saida_stmt; novas_saidas[direcao] = destino
                        loc_data['saidas'] = novas_saidas
                    elif tipo_acao == 'TELEPORTAR': ESTADO_JOGADOR['localizacao_atual'] = valor_acao[0]; exibir_localizacao()
                return

    # 3. PROCESSAMENTO DE COMANDOS GENÉRICOS
    if comando == 'ir':
        if alvo in loc_data.get('saidas', {}):
            ESTADO_JOGADOR['localizacao_atual'] = loc_data['saidas'][alvo]; exibir_localizacao()
        else: print("Não há saída nessa direção.")
    elif comando == 'examinar':
        if alvo in loc_data.get('objetos', {}):
            obj = loc_data['objetos'][alvo]
            print(obj['descricao'])
            if 'revela' in obj and obj['revela'] not in loc_data.get('itens',[]):
                item_revelado = obj.pop('revela')
                loc_data.setdefault('itens', []).append(item_revelado)
                print(f"Algo chama sua atenção: um(a) {ITENS[item_revelado]['nome']} está aqui!")
        elif alvo in ITENS and alvo in ESTADO_JOGADOR['inventario']: print(ITENS[alvo]['descricao'])
        else: print(f"Não há '{alvo}' para examinar aqui.")
    elif comando == 'pegar':
        if alvo in loc_data.get('itens', []):
            loc_data['itens'].remove(alvo); ESTADO_JOGADOR['inventario'].append(alvo)
            print(f"Você pegou: {ITENS[alvo]['nome']}")
        else: print(f"Não há '{alvo}' para pegar aqui.")
    elif comando in ['ecos', 'lembrancas']:
        if not ESTADO_JOGADOR['ecos_coletados']: print("Sua mente está silenciosa... por enquanto.")
        else:
            print("\n--- Ecos da Libertação ---")
            for eco_id in ESTADO_JOGADOR['ecos_coletados']: print(f"[{ECOS[eco_id]['titulo']}]\n   '{ECOS[eco_id]['descricao']}'")
            print("-------------------------")
    elif comando in ['inventario', 'i']:
        if not ESTADO_JOGADOR['inventario']: print("Seu inventário está vazio.")
        else:
            print("Seu inventário:")
            for item_id in ESTADO_JOGADOR['inventario']: print(f"- {ITENS[item_id]['nome']}: {ITENS[item_id]['descricao']}")
    elif comando in ['ajuda', 'help', 'h']:
         print("\nComandos: ir, examinar, pegar, usar, entregar, falar com, inventario, ecos, sair")
    else:
        print("Não entendi esse comando ou nada acontece.")

# --- FUNÇÃO PRINCIPAL ---
def main():
    if not carregar_mundo('jogo_completo.txt'): return
    
    print("\n--- O Domínio de Jurupari ---")
    exibir_localizacao()
    while not ESTADO_JOGADOR['jogo_terminado']:
        try:
            comando_completo = input("\n> ").lower().strip()
        except EOFError: break
        if not comando_completo: continue
        if comando_completo == 'sair': break

        partes = comando_completo.split()
        comando = partes[0]
        alvo = "_".join(partes[1:]) if len(partes) > 1 else None
        
        if len(partes) > 2 and partes[1] == 'com': comando, alvo = partes[0], "_".join(partes[2:])
        if comando == 'i': comando = 'inventario'

        processar_comando(comando, alvo)
    print("\nObrigado por jogar!")

# --- PONTO DE ENTRADA DO JOGO ---
if __name__ == "__main__":
    main()