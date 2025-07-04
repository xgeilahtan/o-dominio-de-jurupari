Projeto 2 – Aventura em Texto: O Domínio de Jurupari  
GRULFAT – Linguagens Formais e Autômatos  
Professor: Thiago Barcelos  
Semestre: 2025.1  

-------------------------------------------------------

Integrantes:  
Lucas Bento – GU3042669  
Maria Eduarda Alves Selvatti – GU3046109  
Nathalie Gonçalves Xavier – GU3046443  

-------------------------------------------------------

📌 Sobre o Projeto  

"O Domínio de Jurupari" é um jogo de aventura em texto, feito em Python, inspirado em lendas do folclore brasileiro. O jogador deve resolver desafios para se redimir de um erro grave cometido contra a floresta.

A estrutura do jogo é baseada em uma **Linguagem de Domínio Específico (DSL)** e um **compilador (lexer + parser)** que interpretam esse universo, aplicando conceitos da disciplina.

-------------------------------------------------------

🗂️ Estrutura dos Arquivos

- `jogo.py` → Motor do jogo: executa o loop principal, controla o inventário, posição e interpreta o mundo.
- `lexer.py` → Analisador léxico com `ply.lex`: transforma o texto DSL em tokens.
- `parser.py` → Analisador sintático com `ply.yacc`: verifica a gramática e gera a AST (árvore de sintaxe abstrata).
- `jogo_completo.txt` → Fonte da DSL: define salas, itens, enigmas, personagens e interações.
- `README.txt` → Este arquivo de instruções.

-------------------------------------------------------

▶️ Como Executar

**Pré-requisitos:**
- Python 3.x instalado
- Biblioteca PLY (`pip install ply`)

**Passos:**
1. Coloque todos os arquivos na mesma pasta.
2. Abra o terminal e navegue até a pasta do projeto:  
   `cd caminho/para/a/pasta/do/projeto`
3. Rode o jogo:  
   `python jogo.py`  
   (ou `python3 jogo.py` se necessário)


-------------------------------------------------------
🌱 Sobre o Jogo  

Você acorda perdido em uma floresta viva, cercado por mistérios e entidades do folclore brasileiro. Após cometer um erro grave contra a natureza, seu único caminho é buscar redenção.  
Para isso, será preciso explorar ambientes místicos, interagir com criaturas lendárias e solucionar enigmas ancestrais.  
Cada escolha importa. Cada item tem um propósito.  
Você será digno do perdão da floresta?

-------------------------------------------------------

🕹️ Comandos do Jogo

O jogo usa comandos simples no formato `verbo <alvo>`. Exemplos:

- `iniciar` → Começa o jogo  
- `ir <direção>` → Move para outra sala (ex: `ir norte`)  
- `examinar <algo>` → Observa um objeto ou personagem  
- `pegar <item>` → Adiciona um item ao inventário  
- `usar <item>` → Usa um item carregado  
- `entregar <item>` → Entrega um item a alguém  
- `falar com <personagem>` → Inicia diálogo  
- `inventario` ou `i` → Lista seus itens  
- `ecos` → Mostra memórias coletadas  
- `mapa` → Abre o mapa no navegador  
- `dica` ou `noob` → Recebe dicas  
- `ajuda` ou `h` → Lista todos os comandos  
- `sair` → Encerra o jogo  

-------------------------------------------------------

Divirta-se explorando o misterioso Domínio de Jurupari! 🌿✨
