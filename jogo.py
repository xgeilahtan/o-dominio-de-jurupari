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
        'alerta_ativo': False, 
        'evento_concluido': False 
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
    objetos_para_exibir = []  # Uma nova lista apenas com os objetos que realmente devem aparecer
    # Pega o estado 'purificada' da sala. Se não existir, considera como False.
    estado_purificada = loc_data.get('estado', {}).get('purificada', False)
    # Itera sobre todos os objetos definidos para a sala
    for obj_id in objetos_disponiveis.keys():
        # Se a sala for a arvore_seca, aplicamos uma regra especial
        if loc_id == 'arvore_seca':
            if obj_id == 'arvore' and not estado_purificada:
                objetos_para_exibir.append(obj_id)
            elif obj_id == 'broto' and estado_purificada:
                objetos_para_exibir.append(obj_id)
        else:
            # Para todas as outras salas, exibe todos os objetos normalmente
            objetos_para_exibir.append(obj_id)

    # No final, imprime apenas os objetos da lista filtrada
    if objetos_para_exibir:
        print("\nVocê também nota:", ", ".join(obj.replace('_', ' ').title() for obj in objetos_para_exibir))

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


  # --- LÓGICA DO EVENTO DO CEMITÉRIO (FASE DE PERIGO) ---
    if loc_id in ['cemiterio_abandonado', 'arvore_seca'] and ESTADO_JOGADOR['evento_cemiterio']['alerta_ativo']:
        
        # Lista de comandos "meta" que não devem causar falha no evento
        comandos_meta = ['dica', 'noob', 'inventario', 'i', 'ecos', 'ajuda', 'help', 'h']

        # Primeiro, verifica se a ação do jogador resolve o evento (sucesso ou fuga)
        if comando == 'usar' and alvo == 'incenso' and 'incenso' in ESTADO_JOGADOR['inventario']:
            print("Lembrando das lendas, você rapidamente acende o incenso...")
            # ... (resto da lógica de sucesso) ...
            ESTADO_JOGADOR['evento_cemiterio']['alerta_ativo'] = False
            if 'mula' not in ESTADO_JOGADOR['ecos_coletados']:
                ESTADO_JOGADOR['ecos_coletados'].append('mula')
                print(f"\nVocê sente um eco (mula) ressoar em sua alma...")
            ESTADO_JOGADOR['evento_cemiterio']['evento_concluido'] = True
            return # O evento acabou, a função para aqui.

        elif comando == 'ir' and alvo == 'sul':
            print("O pânico toma conta de você. Você se vira e corre de volta para a clareira...")
            # ... (resto da lógica de fuga) ...
            ESTADO_JOGADOR['localizacao_atual'] = MUNDO[loc_id]['saidas']['sul']
            ESTADO_JOGADOR['evento_cemiterio']['alerta_ativo'] = False
            ESTADO_JOGADOR['evento_cemiterio']['evento_concluido'] = True
            exibir_localizacao()
            return # O evento acabou, a função para aqui.

        # Se não foi uma ação de sucesso ou fuga, verifica se é um comando "meta"
        elif comando in comandos_meta:
            pass
        
        # Se não for NENHUMA das opções acima, é uma ação de falha.
        else:
            print("Você fica paralisado pelo medo, sem saber o que fazer...")
            print("\nAntes que você possa reagir, o som de cascos trovejantes está em cima de você...")
            ESTADO_JOGADOR['jogo_terminado'] = True
            return # O jogo acabou, a função para aqui.
    
    # 1. Perigos Ambientais (lógica da Iara)
    if loc_id == 'lagoa' and not ESTADO_JOGADOR['estados_ativos']['protegido_da_cancao']:
        
        # Lista de comandos "meta" que não causam morte pela canção
        comandos_meta = ['dica', 'noob', 'inventario', 'i', 'ecos', 'ajuda', 'help', 'h']

        # CONDIÇÃO DE SUCESSO: O jogador se protege
        if comando == 'usar' and alvo == 'cera_de_ouvido' and 'cera_de_ouvido' in ESTADO_JOGADOR['inventario']:
            ESTADO_JOGADOR['estados_ativos']['protegido_da_cancao'] = True
            print("Você rapidamente coloca a cera pegajosa nos ouvidos. O mundo fica abafado e distante. A canção da Iara, antes avassaladora, agora é apenas um murmúrio triste e inofensivo no fundo da sua mente. Você está seguro. No centro da lagoa, a melodia para. Uma figura emerge das águas e te encara.")
            return # O turno de perigo acabou, a função para aqui.
        
        # CONDIÇÃO NEUTRA: O jogador usa um comando seguro
        elif comando in comandos_meta:
            # Se for um comando seguro, não faz nada aqui. A execução continua
            # para o resto da função, onde o comando será de fato processado.
            pass
        
        # CONDIÇÃO DE FALHA: O jogador faz qualquer outra ação de jogo e morre
        else:
            print("A canção domina seus pensamentos. Esquecer... apagar a dor... A água parece quente e convidativa. Você dá um passo, depois outro, e a escuridão líquida te abraça, te puxando para o silêncio eterno do fundo. FIM DE JOGO.")
            ESTADO_JOGADOR['jogo_terminado'] = True
            return # O jogo acabou, a função para aqui.
            
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
        if not alvo:
            print("Pegar o quê?")
            return

        # 1. Primeiro, tenta pegar como um item que já está "solto" na sala.
        if alvo in loc_data.get('itens', []):
            loc_data['itens'].remove(alvo)
            ESTADO_JOGADOR['inventario'].append(alvo)
            print(f"Você pegou: {ITENS[alvo]['nome']}")
        
        # 2. Se não achou, verifica se há um OBJETO com o mesmo nome que pode REVELAR o item.
        elif alvo in loc_data.get('objetos', {}) and loc_data.get('objetos', {})[alvo].get('revela') == alvo:
            # Pega o item diretamente do objeto e o coloca no inventário.
            ESTADO_JOGADOR['inventario'].append(alvo)
            print(f"Você pegou: {ITENS[alvo]['nome']}")
            # Remove a propriedade 'revela' para não ser pego de novo.
            loc_data.get('objetos', {})[alvo].pop('revela')
            # Opcional: Se quiser que o objeto desapareça após pegar o item, descomente a linha abaixo.
            # del loc_data.get('objetos', {})[alvo]

        # 3. Se nenhuma das condições acima funcionou, o item realmente não está disponível.
        else:
            print(f"Não há '{alvo}' para pegar aqui.")

    elif comando == 'usar' and alvo == 'mapa':
        if 'mapa' in ESTADO_JOGADOR['inventario']:
            print("\nVocê abre o pergaminho amarelado... Abrindo o mapa no seu navegador..."); webbrowser.open(URL_MAPA)
        else: print("Você não tem um mapa para usar.")
        return
   # --- LÓGICA ESPECIAL PARA 'USAR MAPA' E 'USAR ECOS' ---
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
    
     # <--- LÓGICA DO COMANDO 'ECOS' ATUALIZADA ---
    elif (comando in ['ecos', 'lembrancas']) or \
     (comando == 'usar' and alvo == 'ecos') or \
     (comando == 'entregar' and alvo == 'ecos'):
        # Comportamento especial se estiver na sala da Mãe de Ouro
        if loc_id == 'mae_de_ouro':
            # --- LÓGICA DO JULGAMENTO FINAL ---
            total_ecos_necessarios = 5 
            ecos_atuais = len(ESTADO_JOGADOR['ecos_coletados'])
            if ecos_atuais >= total_ecos_necessarios:
                print("\nA voz dela soa satisfeita. 'Você mostrou respeito ao pequeno. Negociou com o caótico. Acalmou a dor. Enfrentou o medo. E curou a ferida. Você deu voz aos que foram silenciados...'")
                print("\nA luz na caverna se intensifica, e imagens preenchem sua mente: um machado em suas mãos, a ordem gritada, o som ensurdecedor de uma árvore gigante caindo. A memória volta, clara e dolorosa.")
                print("\n'...mas e a voz que você calou? A voz da Mãe que sangrou por sua ordem, cujo ouro agora corre como lágrimas nas paredes desta mina? Mostre-me que entende o que foi perdido.'")
                print("\nUma parede da caverna se dissolve, revelando uma saída para a luz do dia.")
                print("\n'O caminho está aberto. Vá. E lembre-se que cada árvore tem uma alma.'\n")
                print("FIM DE JOGO (VITÓRIA)")
                ESTADO_JOGADOR['jogo_terminado'] = True
            else:
                print("\nA voz dela é tingida de decepção. 'Você fez o bem, mas seu trabalho não está completo. Uma alma ainda grita na escuridão... um guardião ainda se enfurece... uma canção ainda chora sem consolo. A floresta ainda sente o peso do seu erro.'")
                print("\n'Volte e termine o que começou. O anoitecer se aproxima.'")
                ESTADO_JOGADOR['localizacao_atual'] = 'arvore_seca'
                exibir_localizacao()
            return
        else:
            # Comportamento normal em qualquer outra sala
            if not ESTADO_JOGADOR['ecos_coletados']: print("Sua mente está silenciosa... por enquanto.")
            else:
                print("\n--- Ecos da Libertação ---")
                [print(f"[{ECOS[eco_id]['titulo']}]\n   '{ECOS[eco_id]['descricao']}'") for eco_id in ESTADO_JOGADOR['ecos_coletados']]
                print("-------------------------")
            
    elif comando in ['noob', 'dica']:
        exibir_dicas_noob()
    
    elif comando in ['inventario', 'i']:
        if not ESTADO_JOGADOR['inventario']: print("Seu inventário está vazio.")
        else: print("Seu inventário:"); [print(f"- {ITENS[item_id]['nome']}: {ITENS[item_id]['descricao']}") for item_id in ESTADO_JOGADOR['inventario']]
            
    elif comando in ['ajuda', 'help', 'h']:
        print("\nComandos do Jogo: ir, examinar, pegar, usar, entregar, falar com")
        print("Comandos de Utilidade: inventario (i), ecos, mapa, ajuda (h), dica/noob, iniciar, sair")
         
    else:
        print("Não entendi esse comando.")

    # --- ATUALIZAÇÃO DO CONTADOR DO CEMITÉRIO NO FINAL DO TURNO ---
    if loc_id == 'cemiterio_abandonado' and not ESTADO_JOGADOR['evento_cemiterio']['alerta_ativo']:
        ESTADO_JOGADOR['evento_cemiterio']['contador_acoes'] += 1
        if ESTADO_JOGADOR['evento_cemiterio']['contador_acoes'] >= 4:
            print("\nDe repente, um grito gutural e desumano ecoa pela floresta, vindo de muito longe. Não é um grito de dor, mas um aviso. Um Bradador. O som te causa um arrepio profundo na espinha. Um mal antigo se aproxima. Rápido.")
            ESTADO_JOGADOR['evento_cemiterio']['alerta_ativo'] = True

def exibir_dicas_noob():
    """Analisa o estado do jogo e exibe dicas contextuais, que evoluem com o jogador."""
    
    # --- MODO 1: Dicas Iniciais (Antes do Primeiro Puzzle) ---
    if 'cachimbo_de_barro' not in ESTADO_JOGADOR['inventario'] and 'tela_de_inicio' not in ESTADO_JOGADOR.get('localizacao_atual', ''):
        print("\n--- Sussurros da Floresta ---")
        print("Lendas antigas ecoam em sua mente, fragmentos de sabedoria para sobreviver a esta floresta amaldiçoada:")
        print("\n- O protetor da mata, Curupira, com suas pegadas invertidas, confunde aqueles que não carregam um símbolo de respeito para iluminar o caminho correto.")
        print("- O grito do bradador é um aviso de perigo. Se você ouvir, é melhor correr ou se proteger com algo que te disfarce do galope flamejante.")
        print("- Uma árvore sempre será seca enquanto não houver água para salvá-la.")
        print("- O menino de uma perna só, Saci, é um mestre da travessura e da fumaça. Uma oferenda de bom fumo sempre acalma seu espírito zombeteiro e abre passagens secretas.")
        print("- A canção que emana da lagoa é um feitiço mortal da Iara. Para se aproximar dela, é preciso encontrar uma forma de criar o silêncio absoluto.")
        print("- A velha Cuca, em sua gruta, é uma comerciante de magia. Ela é bem clara quando tenta conversar com ela e anseia por ingredientes raros, como a beleza de uma flor que desafia a própria morte.")
        return # Mostra apenas estas dicas e para.

    # --- MODO 2: Diário de Bordo (Meio/Fim de Jogo) ---
    # Se o jogador já passou do primeiro puzzle, o sistema de dicas se torna mais direto.
    print("\n--- Diário de Bordo da Alma ---")
    
    # Dica de Perigo Iminente (Prioridade Máxima)
    loc_id = ESTADO_JOGADOR.get('localizacao_atual')
    if ESTADO_JOGADOR['evento_cemiterio'].get('alerta_ativo', False):
        if loc_id in ['cemiterio_abandonado', 'arvore_seca']:
            if 'incenso' in ESTADO_JOGADOR['inventario']:
                print("- PERIGO IMINENTE! O grito foi um aviso. Uma fumaça sagrada de certas ervas pode esconder sua presença de um mal antigo. Aja rápido!")
            else:
                print("- PERIGO IMINENTE! O grito foi um aviso. Você não tem nada que possa te proteger ou esconder. Sua única esperança é correr!")
            return

    # Verificação de Puzzles Pendentes
    dica_impressa = False

    if 'cachimbo_de_barro' in ESTADO_JOGADOR['inventario'] and 'incenso' not in ESTADO_JOGADOR['inventario']:
        print("- Um espírito travesso bloqueia a trilha. Ele parece gostar de fumo, e você carrega uma oferenda apropriada.")
        dica_impressa = True
    
    if 'flor_de_cera' in ESTADO_JOGADOR['inventario'] and 'cera_de_ouvido' not in ESTADO_JOGADOR['inventario']:
        print("- A bruxa da gruta deseja uma 'beleza que não murcha'. A flor do cemitério se encaixa na descrição.")
        dica_impressa = True

    if 'cera_de_ouvido' in ESTADO_JOGADOR['inventario'] and 'agua_purificada' not in ESTADO_JOGADOR['inventario']:
        print("- O canto da Iara é mortal. Com os ouvidos protegidos, talvez seja hora de uma conversa com o espírito da lagoa.")
        dica_impressa = True

    if 'agua_purificada' in ESTADO_JOGADOR['inventario'] and not MUNDO.get('arvore_seca', {}).get('estado', {}).get('purificada', False):
        print("- A agonia da árvore seca clama por alívio. A água purificada que você carrega parece ser a única cura.")
        dica_impressa = True

    if len(ESTADO_JOGADOR['ecos_coletados']) < 5: 
        print("- A Mãe de Ouro espera no coração da floresta, mas ela só o julgará quando você tiver provado sua redenção a todos os espíritos.")
        dica_impressa = True

    if not dica_impressa:
        print("Todos os espíritos foram libertados. É hora de encarar a Mãe de Ouro e apresentar os ecos de sua jornada.")

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