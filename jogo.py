# jogo.py
# Versão com o comando 'mapa' abrindo uma URL e condicionado a ter o item.

import parser as game_parser
import webbrowser
import os

# ==============================================================================
# SEÇÃO 1: DADOS GLOBAIS E ESTADO DO JOGADOR
# ==============================================================================

# NOVO: URL do mapa. Lembre-se de colocar o link real da sua imagem aqui.
URL_MAPA = "https://imgur.com/a/teste-eEq6Z58" # <-- SUBSTITUA PELA SUA URL

# Dicionários que serão preenchidos pelo compilador
MUNDO = {}
ITENS = {}
ECOS = {}
INTERACOES = []
VERBOS_DE_INTERACAO = set()

# O estado do jogador, que muda durante o jogo
ESTADO_JOGADOR = {
    'localizacao_atual': 'tela_de_inicio',
    'inventario': [],
    'jogo_terminado': False,
    'estados_ativos': {'protegido_da_cancao': False},
    'ecos_coletados': [],
    'evento_cemiterio': {
        'contador_acoes': 0,
        'alerta_ativo': False 
    }
}


# ==============================================================================
# SEÇÃO 2: COMPILADOR E CARREGADOR DO MUNDO
# ==============================================================================
# (Esta seção não precisa de mudanças)
def compilar_mundo(ast):
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
                    obj_content = {'descricao': stmt_data[1]}
                    if len(stmt_data) > 2 and isinstance(stmt_data[2], dict):
                        obj_content.update(stmt_data[2])
                    room_data['objetos'][stmt_data[0]] = obj_content
                elif stmt_type == 'ESTADO': room_data['estado'][stmt_data[0]] = (stmt_data[1] == 'true')
            MUNDO[data['id']] = room_data
        elif def_type == 'interacao':
            interaction_data = {'verbo': data['verbo'], 'alvo': data['alvo'], 'condicoes': [], 'acoes': []}
            VERBOS_DE_INTERACAO.add(data['verbo'])
            for stmt in data.get('statements', []):
                stmt_type, *stmt_data = stmt
                if stmt_type == 'QUANDO': interaction_data['condicoes'] = stmt_data[0]
                elif stmt_type == 'FAZER': interaction_data['acoes'] = stmt_data[0]
            INTERACOES.append(interaction_data)

def carregar_mundo(caminho_arquivo):
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
    
    # ... (lógica da descrição da sala permanece a mesma)
    if loc_id == 'arvore_seca' and loc_data.get('estado',{}).get('purificada'):
        print(MUNDO['arvore_seca']['objetos'].get('arvore_purificada', {}).get('descricao', loc_data.get('descricao')))
    else:
        print(loc_data.get('descricao', "Não há nada aqui."))

    # <--- NOVO BLOCO PARA EXIBIR NPCs ---
    npcs_na_sala = []
    # Lista de todos os IDs de objetos que são considerados NPCs
    lista_de_npcs_conhecidos = ['cuca', 'iara', 'saci', 'mae_de_ouro', 'curupira'] 
    
    for obj_id in loc_data.get('objetos', {}):
        if obj_id in lista_de_npcs_conhecidos:
            # Pega o nome do objeto, capitaliza e adiciona à lista
            npcs_na_sala.append(obj_id.replace('_', ' ').title())

    if npcs_na_sala:
        print(f"\nNPCs Presentes: {', '.join(npcs_na_sala)}")
    # --- FIM DO NOVO BLOCO ---

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
    """Processa o comando do jogador, com todas as lógicas de evento integradas."""
    loc_id = ESTADO_JOGADOR['localizacao_atual']
    loc_data = MUNDO.get(loc_id, {}) # Usar .get() para evitar erros se a sala não for encontrada

    # --- NOVO: LÓGICA DO JULGAMENTO FINAL ---
    # Verificamos se a interação 'apresentar' ativou o gatilho do julgamento.
    if loc_data.get('estado', {}).get('julgamento_iniciado'):
        loc_data['estado']['julgamento_iniciado'] = False # Desativa o gatilho para não repetir

        # Você definiu 5 ecos no total: curupira, saci, iara, corpo_seco, mula
        total_ecos_necessarios = 5 
        ecos_atuais = len(ESTADO_JOGADOR['ecos_coletados'])

        if ecos_atuais >= total_ecos_necessarios:
            # --- FINAL BOM ---
            print("\nA voz dela soa satisfeita. 'Você mostrou respeito ao pequeno. Negociou com o caótico. Acalmou a dor. Enfrentou o medo. E curou a ferida. Você deu voz aos que foram silenciados...'")
            print("\nA luz na caverna se intensifica, e imagens preenchem sua mente: um machado em suas mãos, a ordem gritada, o som ensurdecedor de uma árvore gigante caindo. A memória volta, clara e dolorosa.")
            print("\n'...mas e a voz que você calou? A voz da Mãe que sangrou por sua ordem, cujo ouro agora corre como lágrimas nas paredes desta mina? Mostre-me que entende o que foi perdido.'")
            print("\nUma parede da caverna se dissolve, revelando uma saída para a luz do dia.")
            print("\n'O caminho está aberto. Vá. E lembre-se que cada árvore tem uma alma.'\n")
            print("FIM DE JOGO (VITÓRIA)")
            ESTADO_JOGADOR['jogo_terminado'] = True
        else:
            # --- FINAL INCOMPLETO ---
            print("\nA voz dela é tingida de decepção. 'Você fez o bem, mas seu trabalho não está completo. Uma alma ainda grita na escuridão... um guardião ainda se enfurece... uma canção ainda chora sem consolo. A floresta ainda sente o peso do seu erro.'")
            print("\n'Volte e termine o que começou. O anoitecer se aproxima.'")
            # Teleporta o jogador de volta para a Árvore Seca
            ESTADO_JOGADOR['localizacao_atual'] = 'arvore_seca'
            exibir_localizacao()
        
        return # O turno é consumido pelo julgamento.
    # --- FIM DA LÓGICA DO JULGAMENTO ---

    # --- LÓGICA DO EVENTO DO CEMITÉRIO (FASE DE PERIGO) ---
    if loc_id == 'cemiterio_abandonado' and ESTADO_JOGADOR['evento_cemiterio']['alerta_ativo']:
        if comando == 'usar' and alvo == 'incenso' and 'incenso' in ESTADO_JOGADOR['inventario']:
            print("Lembrando das lendas, você rapidamente acende o incenso. Uma fumaça com cheiro de mata te envolve, te escondendo dos olhos do mundo sobrenatural. Você se agacha atrás de uma lápide quebrada e espera, o coração martelando no peito.")
            print("\nSegundos depois, um som de trovoada enche o ar. Uma figura aterrorizante galopa pelo cemitério: uma mula em chamas, com fogo jorrando do pescoço. Ela passa furiosamente a poucos metros de você, mas parece não notar sua presença. Tão rápido quanto chegou, ela desaparece no caminho a leste. Você está a salvo.")
            ESTADO_JOGADOR['evento_cemiterio']['alerta_ativo'] = False
            ESTADO_JOGADOR['evento_cemiterio']['contador_acoes'] = 0
            if 'mula' not in ESTADO_JOGADOR['ecos_coletados']:
                ESTADO_JOGADOR['ecos_coletados'].append('mula')
                print(f"\nVocê sente um eco (mula) ressoar em sua alma. Você obteve um Eco da Libertação, digite ecos para analisa-lo.")

        elif comando == 'ir' and alvo == 'sul': 
            print("O pânico toma conta de você. Você se vira e corre de volta para a clareira, sem olhar para trás, enquanto o som de cascos trovejantes se aproxima e o chão treme... Você escapou por um triz, mas a sensação de pavor te persegue.")
            ESTADO_JOGADOR['localizacao_atual'] = MUNDO[loc_id]['saidas']['sul']
            ESTADO_JOGADOR['evento_cemiterio']['alerta_ativo'] = False
            ESTADO_JOGADOR['evento_cemiterio']['contador_acoes'] = 0
            exibir_localizacao()
        else:
            print("Você fica paralisado pelo medo, sem saber o que fazer...")
            print("\nAntes que você possa reagir, o som de cascos trovejantes está em cima de você. Uma mula em chamas, com fogo no lugar da cabeça, irrompe no cemitério. Não há tempo para gritar. Você é atropelado por uma força profana de fogo e fúria. FIM DE JOGO.")
            ESTADO_JOGADOR['jogo_terminado'] = True
        return # O turno do jogador é consumido pelo evento.
    
    # 1. Perigos Ambientais (lógica da Iara)
    if loc_id == 'lagoa' and not ESTADO_JOGADOR['estados_ativos']['protegido_da_cancao']:
        if comando == 'usar' and alvo == 'cera_de_ouvido' and 'cera_de_ouvido' in ESTADO_JOGADOR['inventario']:
            ESTADO_JOGADOR['estados_ativos']['protegido_da_cancao'] = True
            print("Você rapidamente coloca a cera pegajosa nos ouvidos. O mundo fica abafado e distante. A canção da Iara, antes avassaladora, agora é apenas um murmúrio triste e inofensivo no fundo da sua mente. Você está seguro. No centro da lagoa, a melodia para. Uma figura emerge das águas e te encara.")
            return
        else:
            print("A canção domina seus pensamentos. Esquecer... apagar a dor... A água parece quente e convidativa. Você dá um passo, depois outro, e a escuridão líquida te abraça, te puxando para o silêncio eterno do fundo. FIM DE JOGO.")
            ESTADO_JOGADOR['jogo_terminado'] = True
            return
            
    # 2. Interações Específicas (Puzzles do .txt)
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
                            ESTADO_JOGADOR['ecos_coletados'].append(valor_acao[0])
                            print(f"\nVocê sente um eco ({valor_acao[0]}) ressoar em sua alma. Você obteve um Eco da Libertação, digite ecos para analisa-lo.")
                    elif tipo_acao == 'REMOVER_OBJETO': 
                        if valor_acao[0] in loc_data['objetos']: del loc_data['objetos'][valor_acao[0]]
                    elif tipo_acao == 'DEFINIR_ESTADO': loc_data['estado'][valor_acao[0]] = (valor_acao[1] == 'true')
                    elif tipo_acao == 'DEFINIR_SAIDAS': 
                        novas_saidas = {}; [novas_saidas.update({direcao: destino}) for _, direcao, destino in valor_acao[0]]; loc_data['saidas'] = novas_saidas
                    elif tipo_acao == 'TELEPORTAR': ESTADO_JOGADOR['localizacao_atual'] = valor_acao[0]; exibir_localizacao()
                return

    # 3. PROCESSAMENTO DE COMANDOS GENÉRICOS (LÓGICA REESTRUTURADA E CORRIGIDA)
    if comando == 'ir':
        if not alvo: print("Ir para onde?")
        elif alvo in loc_data.get('saidas', {}): ESTADO_JOGADOR['localizacao_atual'] = loc_data['saidas'][alvo]; exibir_localizacao()
        else: print("Não há saída nessa direção.")
    
    elif comando == 'examinar':
        if not alvo: print("Examinar o quê?")
        elif alvo in loc_data.get('objetos', {}):
            obj = loc_data['objetos'][alvo]; print(obj['descricao'])
            if 'revela' in obj and obj['revela'] not in loc_data.get('itens',[]):
                item_revelado = obj.pop('revela'); loc_data.setdefault('itens', []).append(item_revelado); print(f"Algo chama sua atenção: um(a) {ITENS[item_revelado]['nome']} está aqui!")
        elif alvo in ITENS and alvo in ESTADO_JOGADOR['inventario']: print(ITENS[alvo]['descricao'])
        else: print(f"Não há '{alvo}' para examinar aqui.")
            
    elif comando == 'pegar':
        if not alvo: print("Pegar o quê?")
        elif alvo in loc_data.get('itens', []): loc_data['itens'].remove(alvo); ESTADO_JOGADOR['inventario'].append(alvo); print(f"Você pegou: {ITENS[alvo]['nome']}")
        else: print(f"Não há '{alvo}' para pegar aqui.")

    elif comando == 'usar' and alvo == 'mapa':
        if 'mapa' in ESTADO_JOGADOR['inventario']:
            print("\nVocê abre o pergaminho amarelado... Abrindo o mapa no seu navegador..."); webbrowser.open(URL_MAPA)
        else: print("Você não tem um mapa para usar.")
        return

    elif comando == 'usar':
        if not alvo: print("Usar o quê?")
        else: print("Nada acontece.")

    elif comando == 'entregar':
        if not alvo: print("Entregar o quê?")
        else: print("Nada acontece.")

    elif comando == 'falar': # Corrigido para não incluir o 'com'
        if not alvo: print("Falar com quem?")
        else: print("Nada acontece.")
    
    elif comando in ['ecos', 'lembrancas']:
        if not ESTADO_JOGADOR['ecos_coletados']: print("Sua mente está silenciosa... por enquanto.")
        else: print("\n--- Ecos da Libertação ---"); [print(f"[{ECOS[eco_id]['titulo']}]\n   '{ECOS[eco_id]['descricao']}'") for eco_id in ESTADO_JOGADOR['ecos_coletados']]; print("-------------------------")
            
    elif comando in ['inventario', 'i']:
        if not ESTADO_JOGADOR['inventario']: print("Seu inventário está vazio.")
        else: print("Seu inventário:"); [print(f"- {ITENS[item_id]['nome']}: {ITENS[item_id]['descricao']}") for item_id in ESTADO_JOGADOR['inventario']]
            
    elif comando in ['ajuda', 'help', 'h']:
         print("\nComandos: ir, examinar, pegar, usar, entregar, falar com, inventario, ecos, mapa, iniciar, sair")
         
    else:
        print("Não entendi esse comando.")

    # --- ATUALIZAÇÃO DO CONTADOR DO CEMITÉRIO NO FINAL DO TURNO ---
    if loc_id == 'cemiterio_abandonado' and not ESTADO_JOGADOR['evento_cemiterio']['alerta_ativo']:
        ESTADO_JOGADOR['evento_cemiterio']['contador_acoes'] += 1
        if ESTADO_JOGADOR['evento_cemiterio']['contador_acoes'] >= 4:
            print("\nDe repente, um grito gutural e desumano ecoa pela floresta, vindo de muito longe. Não é um grito de dor, mas um aviso. Um Bradador. O som te causa um arrepio profundo na espinha. Um mal antigo se aproxima. Rápido.")
            ESTADO_JOGADOR['evento_cemiterio']['alerta_ativo'] = True
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