# 📡 Protocolo de Revezamento Binário TCP

> Implementação de um sistema distribuído de mensageria com protocolo binário customizado, focado na resolução de fragmentação de rede e serialização manual de bytes.

Projeto desenvolvido como **Tarefa Avaliativa** para a disciplina de **Computação Distribuída**.

---

## 🏗️ Arquitetura e Funcionamento

O sistema opera no modelo de **Revezamento Distribuído (Relay Chat)** com três papéis distintos:

```
┌─────────────┐     bytes     ┌──────────────────┐     bytes     ┌─────────────┐
│  Cliente A  │ ──────────►  │     Servidor     │ ──────────►  │  Cliente B  │
│  (Produtor) │              │  (Middleware /   │              │ (Consumidor)│
└─────────────┘              │     Broker)      │              └─────────────┘
  Conecta, envia             │  Fila FIFO       │              Conecta, lê e
  e desconecta.              │  na memória      │              desconecta.
                             └──────────────────┘
```

| Papel | Responsabilidade |
|---|---|
| **Cliente A** (Produtor) | Conecta ao servidor, envia uma mensagem encapsulada em bytes e desconecta |
| **Servidor** (Middleware) | Recebe os bytes, trata fragmentações TCP, desempacota e armazena em fila FIFO |
| **Cliente B** (Consumidor) | Conecta solicitando leitura; o servidor entrega a mensagem mais antiga da fila |

---

## 📦 Protocolo Binário Customizado

Para otimizar o tráfego na Camada de Transporte, o envio de strings puras foi substituído por um **empacotamento binário rígido** utilizando a biblioteca `struct` nativa do Python.

Cada pacote possui um **Header estrito de 3 bytes**:

```
┌──────────────────┬────────────┬──────────────────────────────┐
│  Payload Size    │  Operação  │           Payload            │
│    (2 bytes)     │  (1 byte)  │          (variável)          │
├──────────────────┼────────────┼──────────────────────────────┤
│ Inteiro Big-     │ 0x00 SEND  │ Conteúdo em UTF-8            │
│ endian com o     │ 0x01 RECV  │ (presente apenas se 0x00)    │
│ tamanho exato    │            │                              │
└──────────────────┴────────────┴──────────────────────────────┘
```

### Tratamento de Fragmentação TCP

O TCP é um protocolo orientado a **fluxo de bytes** (*stream*), o que significa que os dados podem ser fragmentados durante o tráfego. Para garantir a integridade, o servidor:

1. Lê **rigorosamente** os primeiros 3 bytes com `readexactly(3)`
2. Extrai o `Payload Size` do header
3. Só então realiza a leitura do restante do pacote

Isso evita bloqueios ou corrupção de dados em redes com latência variável.

---

## 🚀 Como Executar

Abra **três instâncias de terminal** para simular os nós da rede:

**1. Inicie o Servidor:**
```bash
python Entregavel1-Server.py
```
> O servidor fará o bind em `0.0.0.0:8080`, aguardando conexões.

**2. Envie uma mensagem (Cliente A — Produtor):**
```bash
python Entregavel1-Client-A.py
```

**3. Recupere a mensagem (Cliente B — Consumidor):**
```bash
python Entregavel1-Client-B.py
```

---

## 🧠 Decisões de Engenharia: Síncrono vs. Assíncrono

O Servidor foi implementado de forma **assíncrona** (`asyncio`), enquanto os Clientes foram mantidos **síncronos** (`socket`). Essa escolha foi intencional.

### Por que os clientes são síncronos agora?

O papel dos Clientes A e B é executar uma ação de **"tiro único"**: conectar, enviar (ou receber) um pequeno pacote de bytes e encerrar. Como o cliente lida com apenas uma conexão por vez, ele não sofre do *Problema C10K* que afeta servidores. Adicionar um Event Loop do `asyncio` ao cliente seria um overhead desnecessário para o escopo atual.

### Como seria a migração para assíncrono?

Se o escopo crescer e o cliente precisar de tarefas simultâneas — como manter uma GUI responsiva, enviar *heartbeats* ou gerenciar dezenas de conexões (modelo P2P) — o modelo síncrono travaria a aplicação inteira a cada `socket.recv()`.

A migração substituiria a biblioteca `socket` padrão pela API de alto nível do `asyncio`:

```python
# ❌ Modelo Atual (Síncrono — bloqueante)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', 8080))
    s.sendall(pacote_completo)
```

```python
# ✅ Modelo Futuro (Assíncrono — não-bloqueante)
reader, writer = await asyncio.open_connection('127.0.0.1', 8080)
writer.write(pacote_completo)
await writer.drain()  # Libera a CPU enquanto os dados trafegam
```

Isso permitiria ao cliente **delegar a espera da rede ao Kernel do SO**, mantendo a CPU livre para processar outras tarefas concorrentes.
