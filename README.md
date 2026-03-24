Protocolo de Revezamento Binário TCP
====================================

Este repositório contém a implementação de um sistema distribuído de mensageria. O projeto consiste em um servidor TCP assíncrono e clientes síncronos que se comunicam através de um protocolo binário customizado, focado na resolução de fragmentação de rede e serialização manual de bytes.

Projeto desenvolvido como Tarefa Avaliativa para a disciplina de Computação Distribuída.

🏗️ Arquitetura e Funcionamento
-------------------------------

O sistema opera no modelo de **Revezamento Distribuído** (Relay Chat):

1.  **Cliente A (Produtor):** Conecta ao servidor, envia uma mensagem encapsulada em bytes e desconecta.
    
2.  **Servidor (Middleware/Broker):** Recebe os bytes, trata possíveis fragmentações do TCP, desempacota a mensagem e a armazena em uma fila na memória (FIFO).
    

📦 O Protocolo Binário Customizado
----------------------------------

Para otimizar o tráfego na Camada de Transporte, o envio de _strings_ puras foi substituído por um empacotamento binário rígido utilizando a biblioteca struct nativa do Python.

Cada pacote enviado na rede possui um **Cabeçalho (Header) estrito de 3 bytes**:

**CampoTamanhoDescriçãoPayload Size**2 Bytes

Inteiro (Big-endian) indicando o tamanho exato da mensagem em bytes que vem a seguir.

**Operação**1 Byte

0x00 para ENVIAR (armazenar no servidor) / 0x01 para RECUPERAR (ler do servidor).

**Dados (Payload)**Variável

O conteúdo da mensagem codificado em UTF-8 (presente apenas se a Operação for 0x00).

Tratamento de Fragmentação TCP
------------------------------

Como o TCP é um protocolo orientado a fluxo de bytes (stream), os dados podem sofrer fragmentação. Para garantir a integridade, o servidor lê rigorosamente os 3 primeiros bytes (readexactly(3)) para extrair o Payload Size. Somente após essa validação, ele executa a leitura do restante do pacote, evitando bloqueios ou corrupção de dados caso a rede esteja lenta.

🚀 Como Executar
----------------

Abra três instâncias de terminal para simular os nós da rede:

**1\. Inicie o Servidor:**

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python Entregavel1-Server.py   `

O servidor fará o bind em 0.0.0.0:8080, aguardando conexões.

**2\. Envie uma mensagem (Cliente A):**

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python Entregavel1-Client-A.py   `

**3\. Recupere a mensagem (Cliente B):**

Bash

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python Entregavel1-Client-B.py   `

🧠 Decisões de Engenharia: Síncrono vs. Assíncrono
--------------------------------------------------

Nesta arquitetura, **o Servidor foi implementado de forma assíncrona** (asyncio), enquanto **os Clientes foram mantidos síncronos** (socket).

Por que manter os clientes síncronos agora?
-------------------------------------------

A escolha pelo modelo síncrono no cliente prioriza a **simplicidade arquitetônica**. O papel dos Clientes A e B neste escopo é executar uma ação de "tiro único": conectar, enviar (ou receber) um pequeno pacote de bytes e encerrar. Como o cliente lida com apenas uma conexão por vez, ele não sofre do problema de bloqueio de CPU (Problema C10K) que assombra os servidores. Inserir um _Event Loop_ do asyncio no cliente adicionaria um _overhead_ de configuração desnecessário para o requisito atual.

Por que (e como) transformar os clientes em assíncronos no futuro?
------------------------------------------------------------------

Se o escopo do projeto crescer e o cliente precisar realizar múltiplas tarefas simultâneas — como manter uma interface gráfica (GUI) responsiva, enviar _heartbeats_ (sinais de vida) constantes para o servidor, ou manter dezenas de conexões com diferentes nós simultaneamente (como em um nó P2P puro) —, o modelo síncrono travaria a aplicação inteira a cada socket.recv().

**Como seria a transformação:**

Para migrar o cliente para o modelo assíncrono, substituiríamos a biblioteca socket padrão pela API de alto nível do asyncio. A estrutura de conexão mudaria de:

Python

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # Modelo Atual (Síncrono bloqueante)  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:      s.connect(('127.0.0.1', 8080))      s.sendall(pacote_completo)   `

Para:

Python

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   # Modelo Assíncrono (Não-bloqueante)  reader, writer = await asyncio.open_connection('127.0.0.1', 8080)  writer.write(pacote_completo)  await writer.drain() # Libera a CPU enquanto os dados trafegam   `

Isso permitiria ao cliente delegar a espera da rede ao Kernel do sistema operacional, mantendo a CPU livre para processar outras tarefas concorrentes.

Se precisar ajustar algum termo específico para se alinhar ao padrão dos seus outros repositórios, informe. Posso instruir sobre os próximos passos da disciplina, como a transição para filas de mensagens (RabbitMQ) ou memória compartilhada (Redis), caso seja o rumo do semestre.
