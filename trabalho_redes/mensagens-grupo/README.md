# Instruções de Execução — Sistema de Mensagens

## Visão Geral

O projeto é composto por três arquivos Python que formam um sistema de mensagens produtor-consumidor.

- **Server.py** — servidor central que recebe mensagens e as redistribui
- **ClienteTeclado.py** — cliente produtor, responsável por enviar mensagens
- **ClienteTela.py** — cliente consumidor, responsável por exibir as mensagens recebidas

## Portas Utilizadas

| Componente       | Porta |
|------------------|-------|
| ClienteTeclado   | 9002  |
| ClienteTela      | 9003  |

Essas portas devem estar livres antes de iniciar o servidor.

## Ordem de Execução

### 1. Iniciar o Servidor

Executar no terminal:

```bash
python Server.py
```

O servidor ficará aguardando conexões nas portas 9002 e 9003. A saída esperada é:

```
[*] Aguardando Teclados na porta 9002...
[*] Aguardando Telas na porta 9003...
```

### 2. Iniciar o Cliente de Tela (Consumidor)

Abra um segundo terminal e execute:

```bash
python ClienteTela.py
```

Este cliente se conecta ao servidor na porta 9003 e ficará monitorando as mensagens enviadas por qualquer teclado conectado.

### 3. Iniciar o Cliente de Teclado (Produtor)

Abra um terceiro terminal e execute:

```bash
python ClienteTeclado.py
```

Ao conectar, o servidor solicitará um nickname. Após informá-lo, você poderá digitar mensagens livremente.

## Uso

- Digite qualquer texto no terminal do **ClienteTeclado** e pressione Enter para enviar a mensagem.
- A mensagem aparecerá formatada no terminal do **ClienteTela**, no seguinte formato:

```
[NickName (127.0.0.1) 14:32:05]: conteúdo da mensagem
```

- Para encerrar o ClienteTeclado, digite:

```
sair
```
## Comportamento em Caso de Falha

- Se o **ClienteTeclado** for iniciado antes do servidor, ele tentará reconectar automaticamente a cada 2 segundos.
- Se a conexão do **ClienteTeclado** cair durante o uso, ele tentará reconectar automaticamente.
- Se um **ClienteTela** se desconectar, o servidor o remove da lista de destinatários sem interromper os demais.
