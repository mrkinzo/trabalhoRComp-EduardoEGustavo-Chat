# Chat via Sockets — Documentação da Aplicação

Aplicação de chat em tempo real baseada em **sockets TCP** com arquitetura **produtor-consumidor**, implementada em Python. O sistema é composto por três arquivos independentes que se comunicam através de um servidor central.

---

## Visão Geral da Arquitetura

```
[ClienteTeclado.py]  →  porta 9002  →  [Server.py]  →  porta 9003  →  [ClienteTela.py]
    (Produtor)                          (Servidor)                       (Consumidor)
```

O servidor atua como intermediário: recebe mensagens dos clientes **Teclado** (produtores) e as distribui para todos os clientes **Tela** (consumidores) conectados.

---

##  Descrição dos Arquivos

### 1. `Server.py` — Servidor Central

O núcleo da aplicação. Gerencia simultaneamente as conexões de entrada (produtores) e saída (consumidores), mantendo uma **fila de mensagens compartilhada** entre as threads.

**Responsabilidades:**
- Escuta na porta `9002` conexões de clientes Teclado
- Escuta na porta `9003` conexões de clientes Tela
- Mantém uma fila (`FILA`) com as mensagens recebidas
- Distribui as mensagens para todos os clientes Tela conectados (broadcast)

**Principais componentes internos:**

| Componente | Descrição |
|---|---|
| `FILA` | Lista compartilhada que armazena as mensagens aguardando envio |
| `CLIENTES_TELA` | Lista com os sockets de todos os consumidores conectados |
| `SEMAFORO_ACESSO_FILA` | Semáforo binário que protege o acesso exclusivo à fila |
| `SEMAFORO_ITENS_FILA` | Semáforo contador que sinaliza quando há itens na fila |
| `SEMAFORO_CLIENTES` | Semáforo binário que protege a lista de clientes Tela |

**Threads em execução:**

| Thread | Função | Descrição |
|---|---|---|
| `t1` | `escutar_teclado()` | Aceita novos produtores na porta 9002 |
| `t2` | `gerenciar_telas()` | Aceita novos consumidores na porta 9003 |
| `t3` | `thread_distribuidora()` | Consome a fila e faz broadcast para as Telas |

**Fluxo de uma mensagem:**
1. Um Teclado envia uma mensagem → `atender_produtor()` a recebe
2. A mensagem é formatada com nickname, IP e horário
3. `produzir()` adiciona à fila e libera o semáforo de itens
4. `thread_distribuidora()` desbloqueia, consome o item e envia para todas as Telas

**Formato da mensagem gerada:**
```
[Nickname (IP) HH:MM:SS]: texto da mensagem
```

---

### 2. `ClienteTeclado.py` — Cliente Produtor

Interface de entrada do usuário. Permite que uma pessoa envie mensagens ao servidor através do terminal, funcionando como um **produtor** na arquitetura.

**Responsabilidades:**
- Conecta-se ao servidor na porta `9002`
- Solicita e envia o **Nickname** do usuário ao servidor
- Lê mensagens digitadas no terminal e as envia ao servidor
- Aguarda confirmação (`OK`) do servidor após cada envio
- Tenta **reconectar automaticamente** em caso de queda de conexão

**Fluxo de execução:**
1. Tenta conectar ao servidor (repete a cada 2 segundos até conseguir)
2. Recebe a pergunta do nickname e o envia
3. Entra em loop de leitura: lê do terminal → envia → aguarda `OK`
4. Digitar `sair` encerra o cliente

**Tratamento de erros:**
- `ConnectionRefusedError`: servidor offline → aguarda e tenta novamente
- `BrokenPipeError` / `ConnectionResetError`: conexão perdida → reconecta automaticamente

---

### 3. `ClienteTela.py` — Cliente Consumidor

Interface de exibição das mensagens. Conecta-se ao servidor e fica aguardando mensagens para exibi-las no terminal, funcionando como um **consumidor** na arquitetura.

**Responsabilidades:**
- Conecta-se ao servidor na porta `9003`
- Fica em escuta contínua, aguardando mensagens chegarem do servidor
- Exibe cada mensagem recebida formatada no terminal

**Fluxo de execução:**
1. Conecta ao servidor na porta 9003
2. Entra em loop de recebimento
3. Cada mensagem recebida é impressa com uma linha separadora visual

**Tratamento de erros:**
- `ConnectionRefusedError`: exibe aviso se o servidor não estiver online
- Detecta desconexão do servidor (dados vazios) e encerra graciosamente

---
## Como Executar

Execute cada arquivo em um terminal separado, **nesta ordem:**

```bash
# 1. Inicie o servidor
python Server.py

# 2. Conecte uma ou mais Telas (consumidores)
python ClienteTela.py

# 3. Conecte um ou mais Teclados (produtores)
python ClienteTeclado.py
```

> É possível conectar **múltiplos Teclados e múltiplas Telas** simultaneamente. Todas as Telas recebem as mensagens de todos os Teclados em tempo real.

---

##  Configurações de Porta

| Arquivo | HOST | Porta |
|---|---|---|
| `Server.py` | `0.0.0.0` (todas as interfaces) | 9002 (entrada) e 9003 (saída) |
| `ClienteTeclado.py` | `127.0.0.1` | 9002 |
| `ClienteTela.py` | `127.0.0.1` | 9003 |

---

## Concorrência e Semáforos

O servidor utiliza **semáforos** da biblioteca `threading` para garantir acesso seguro aos recursos compartilhados entre múltiplas threads, evitando condições de corrida:

- **`SEMAFORO_ACESSO_FILA`** (Semaphore(1)): garante exclusão mútua na leitura/escrita da fila
- **`SEMAFORO_ITENS_FILA`** (Semaphore(0)): bloqueia o consumidor quando a fila está vazia, desbloqueando a cada novo item produzido
- **`SEMAFORO_CLIENTES`** (Semaphore(1)): protege a lista de clientes Tela durante adição e remoção
