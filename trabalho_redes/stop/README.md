# Instruções de Execução — Jogo Stop

## Visão Geral

- **Server.py** — servidor central que gerencia as rodadas, recebe respostas e calcula pontuações
- **ClienteTeclado.py** — cliente jogador, responsável por enviar respostas e visualizar o andamento da partida
- **ClienteTela.py** — cliente espectador, responsável apenas por acompanhar as pontuações sem participar

## Configurações da Partida

Os seguintes valores podem ser ajustados diretamente no arquivo **Server.py**:

| Parametro    | Variavel       | Valor Padrao                          |
|--------------|----------------|---------------------------------------|
| Jogadores    | `N_JOGADORES`  | 2                                     |
| Rodadas      | `N_RODADAS`    | 2                                     |
| Temas        | `TEMAS`        | Nome, Cidade, Animal, Objeto          |
| Porta        | `PORTA`        | 9002                                  |

## Ordem de Execução


### 1. Iniciar o Servidor

Abra um terminal e execute:

```bash
python Server.py
```

O servidor ficará aguardando a conexão dos jogadores. A saída esperada é:

```
Servidor está aguardando jogadores
```

### 2. Iniciar os Clientes Jogadores

Abra um terminal para cada jogador e execute:

```bash
python ClienteTeclado.py
```

Ao conectar, o servidor solicitará o nome do jogador. A partida só inicia quando o numero de jogadores definido estiver conectado.

### 3. Iniciar o Cliente Espectador (opcional)

Abra um terminal e execute:

```bash
python ClienteTela.py
```

Este cliente se conecta ao servidor e acompanha as pontuações sem participar das rodadas.

## Uso

A cada rodada, o servidor sorteia uma letra e envia os temas para todos os jogadores:

```
Rodada 1 - Letra: B

TEMAS: Nome, Cidade, Animal, Objeto
Digite suas respostas:
```

O jogador deve digitar uma resposta para cada tema, separadas por virgula, e pressionar Enter:

```
Bruno, Brasilia, Baleia, Bola
```

Ao final de cada rodada, o servidor calcula os pontos e exibe a pontuacao atualizada para todos:

```
Pontuacoes:
Bruno: 3
Carlos: 6

Vencedor: Carlos
```

## Calculo de Pontuacao

- Resposta unica (nenhum outro jogador respondeu igual): **3 pontos**
- Resposta repetida (outro jogador respondeu igual): **1 ponto**

## Comportamento em Caso de Falha

- Se um cliente tentar se conectar antes do servidor estar ativo, a conexão será recusada e uma mensagem de erro será exibida.
- Se um cliente se desconectar durante a partida, o servidor pode travar aguardando a resposta do jogador ausente, pois o sistema exige que todos respondam antes de avançar de rodada.