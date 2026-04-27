import socket
import threading
from datetime import datetime
import random

HOST = "0.0.0.0"
PORTA = 9002

N_JOGADORES = 2 # Quantidade mínima de jogadores para iniciar a partida.
N_RODADAS = 2 # Define o número de rodadas por partida.

CLIENTES = [] # Lista que guarda os clientes conectados.
RESPOSTAS = [] # Lista que guarda as respostas dos jogadores.
PONTUACOES = {} # Lista que guarda a pontuação de cada jogador.

# Garante que apenas uma thread acesse a lista de clientes por vez.
SEMAFORO_CLIENTES = threading.Semaphore(1) 
# Garante que apenas uma thread acesse a lista de respostas por vez.
SEMAFORO_RESPOSTAS = threading.Semaphore(1) 
# Controla se todos os clientes estão conectados.
SEMAFORO_TODOS_CONECTADOS = threading.Semaphore(0)
# Controla se todos os clientes responderam.
SEMAFORO_TODOS_RESPONDERAM = threading.Semaphore(0)
# Garante que que apenas uma thread sorteie a letra por vez.
SEMAFORO_LETRA = threading.Semaphore(1)
# Avisa que a letra foi sorteada e pode ser enviada.
SEMAFORO_LETRA_PRONTA = threading.Semaphore(0)

TEMAS = ["Nome", "Cidade", "Animal", "Objeto"]
LETRA_RODADA = [""] # Lista para guardar a letra sorteada - é vazia pois o valor é atualizado a cada rodada, e precisa ser mutável para que as threads possam acessar a letra sorteada.

# Envia mensagem para todos os clientes.
def broadcast(msg):

    SEMAFORO_CLIENTES.acquire() # Bloqueia o acesso à lista de clientes para não ser modificada enquanto está em uso
    for c in CLIENTES:
        # Tenta enviar a mensagem para o cliente, se der erro, ele ignora, pois os erros de conexão são tratados em threds individuais.
        try: 
            c["conn"].sendall(msg.encode("utf-8"))
        except:
            pass

    SEMAFORO_CLIENTES.release() # Libera o acesso à lista de clientes para outras threads.


# Gerencia o ciclo de um jogador : cadastro, rodadas e pontuação.
def atender_cliente(conn, addr):

    global RESPOSTAS

    # Com a conexão estabelecida...
    with conn:
        # Pede o nome dos jogadores e recebe-os.
        conn.sendall("Digite seu nome: ".encode("utf-8"))
        nome = conn.recv(1024).decode("utf-8").strip()

        # Adiciona os jogadores, registrando a conexão, o nome e o endereço do jogador.
        SEMAFORO_CLIENTES.acquire()
        CLIENTES.append({"conn": conn, "nome": nome, "addr": addr})
        PONTUACOES[nome] = 0 # Registra o nome do jogador na lista de pontuações.

        # Se a quantidade de jogadores for atingida, libera todas as threads.
        if len(CLIENTES) == N_JOGADORES:
            for _ in range(N_JOGADORES):
                SEMAFORO_TODOS_CONECTADOS.release()
        SEMAFORO_CLIENTES.release()
        SEMAFORO_TODOS_CONECTADOS.acquire() # Espera todos entrarem.

        # Percorre todas as rodadas.
        for rodada in range(N_RODADAS):
            SEMAFORO_LETRA.acquire()
            # Apenas o primeiro jogador sorteia a letra, para que todos recebam a mesma opção na rodada.
            if CLIENTES[0]["nome"] == nome:
                letra = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
                # Armazena a letra na lista de letras.
                LETRA_RODADA[0] = letra
                # Formata a mensagem da rodada, com o número da rodada, a letra, e os temas.
                msg_rodada = (
                    f"\nRodada {rodada+1} - Letra: {letra}\nTEMAS: {', '.join(TEMAS)}\n"
                )
                # Libera todos os jogadores para receberem.
                for _ in range(N_JOGADORES):
                    SEMAFORO_LETRA_PRONTA.release()
                SEMAFORO_LETRA.release()
            else:
                SEMAFORO_LETRA.release()

            # Todos esperam a letra estar pronta.
            SEMAFORO_LETRA_PRONTA.acquire()

            # Envia para cada cliente individualmente.
            conn.sendall(
                f"\nRodada {rodada+1} - Letra: {LETRA_RODADA[0]}\nTEMAS: {', '.join(TEMAS)}\n".encode(
                    "utf-8"
                )
            )

            # Recebe as respostas dos jogadores.
            data = conn.recv(4096).decode("utf-8")

            # Formata respostas recebidas, com o nome do jogador, endereço,
            # horário que a mensagem foi recebida e o texto da mensagem.
            horario = datetime.now().strftime("%H:%M:%S")
            msg_formatada = f"[{nome} ({addr[0]}) {horario}]: {data}"

            # Divide a resposta em uma lista, pra cada palavra corresponder a um tema.
            respostas = data.strip().split(",")

            # Trava o acesso à lista de respostas e adiciona elas na lista, com o nome do jogador e sua resposta.
            SEMAFORO_RESPOSTAS.acquire()
            RESPOSTAS.append((nome, respostas))
            # Verifica se todos os jogadores responderam.
            if len(RESPOSTAS) == N_JOGADORES:
                # Percorre cada jogador e para cada um libera o semáforo.
                for _ in range(N_JOGADORES):
                    SEMAFORO_TODOS_RESPONDERAM.release()
            # Libera o acesso    à lista de respostas.
            SEMAFORO_RESPOSTAS.release()

            # A thread para e só continua se todos responderam
            SEMAFORO_TODOS_RESPONDERAM.acquire()

            # Faz o cálculo da pontuação e manda para todos.
            if nome == CLIENTES[0]["nome"]:
                calcular_pontos()
                enviar_pontuacoes()

            # Threads esperam para ninguém avançar sem que o cálculo tenha terminado.
            SEMAFORO_TODOS_RESPONDERAM.acquire()


# Calcula a pontuação dos jogadores.
def calcular_pontos():
    global RESPOSTAS

    # Percorre cada tema.
    for i in range(len(TEMAS)):
        # Pega as respostas dos jogadores.
        respostas_coluna = [r[1][i].strip().lower() for r in RESPOSTAS]

        # Percorre cada jogador
        for nome, respostas in RESPOSTAS:
            # Pega a resposta do jogador na categoria específica
            resposta = respostas[i].strip().lower()
            # Verifica se a resposta é unica - se for recebe 3 pontos, senão recebe 1 ponto.
            if respostas_coluna.count(resposta) == 1:
                PONTUACOES[nome] += 3
            else:
                PONTUACOES[nome] += 1

    # Reinicia as respostas para a próxima rodada.
    RESPOSTAS = []


# Envia as pontuações para todos os jogadore.
def enviar_pontuacoes():

    resultado = "\nPontuações:\n"
    # Percorre todos os jogadores.
    for nome, pontos in PONTUACOES.items():
        # Coloca a pontuação e o nome no resultado de cada jogador.
        resultado += f"{nome}: {pontos}\n"

    # Encontra quem tem mais pontos (nome com o maior valor).
    vencedor = max(PONTUACOES, key=PONTUACOES.get)
    # Adiciona o vencedor no resultado.
    resultado += f"\nVencedor: {vencedor}\n"

    # Envia a mensagem para todos os jogadores.
    broadcast(resultado)


# Inicia o servidor.
def iniciar_servidor():
    # Cria a conexão, que termina quando o socket é fechado.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Tenta estabelecer a conexão na porta definida.
        s.bind((HOST, PORTA))
        s.listen()
        print("Servidor está aguardando jogadores")

        #mantém o servidor rodando para novos jogadores se conectarem mesmo durante a partida.
        while True:
            # Aceita pedidos de conexão.
            conn, addr = s.accept()
            # Cria uma thread para atender o cliente conectado.
            threading.Thread(
                target=atender_cliente, args=(conn, addr), daemon=True
            ).start()


if __name__ == "__main__":
    iniciar_servidor()
