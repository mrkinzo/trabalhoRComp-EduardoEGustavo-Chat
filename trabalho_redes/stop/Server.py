import socket
import threading
from datetime import datetime
import random

HOST = "0.0.0.0"
PORTA = 9002

# Define a quantidade de jogadores necessários para começar.
N_JOGADORES = 2
# Define o número de rodadas.
N_RODADAS = 2

# Cria uma lista que guarda os clientes que estão jogando.
CLIENTES = []
# Cria uma lista que guarda as respostas das rodadas.
RESPOSTAS = []
# Cria uma lista que guarda a pontuação de cada jogador.
PONTUACOES = {}

# Cria um semáforo que controla o acesso à lista de clientes - definindo 1 thread por vez.
SEMAFORO_CLIENTES = threading.Semaphore(1)
# Cria um semáforo que controla o acesso à lista de respostas - definindo 1 thread por vez.
SEMAFORO_RESPOSTAS = threading.Semaphore(1)
# Cria um semáforo que controla a conexão dos clientes - é bloqueadao até todos conectarem.
SEMAFORO_TODOS_CONECTADOS = threading.Semaphore(0)
# Cria um semáforo que controla se todos os clientes responderam - é bloqueadao até todos responderem.
SEMAFORO_TODOS_RESPONDERAM = threading.Semaphore(0)

# Cria uma lista que define os temas que serão usados no jogo.
TEMAS = ["Nome", "Cidade", "Animal", "Objeto"]

# Cria a função que envia as mensagens para todos.
def broadcast(msg):

    # Tenta acessar a lista de clientes.
    SEMAFORO_CLIENTES.acquire()
    # Percorre todos os clientes.
    for c in CLIENTES:
        # Tenta enviar a mensagem, se houver exceção ele para.
        try:
            c["conn"].sendall(msg.encode("utf-8"))
        except:
            pass
    # Libera a lista de clientes.
    SEMAFORO_CLIENTES.release()

# Cria a função que roda os clientes.
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
        # Inicializa a pontuação do jogador em 0.
        PONTUACOES[nome] = 0

        # Se a quantidade de jogadores for atingida, libera todas as threads.
        if len(CLIENTES) == N_JOGADORES:
            for _ in range(N_JOGADORES):
                SEMAFORO_TODOS_CONECTADOS.release()
        SEMAFORO_CLIENTES.release()
        # Espera todos entrarem.
        SEMAFORO_TODOS_CONECTADOS.acquire()

        # Percorre todas as rodadas.
        for rodada in range(N_RODADAS):
            # Faz o sorteio das letras.
            letra = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
            # Envia os dados da rodada - número da rodada, letra sorteada e os temas que serão respondidos.
            conn.sendall(f"\nRodada {rodada+1} - Letra: {letra}\n".encode("utf-8"))
            conn.sendall(f"TEMAS: {', '.join(TEMAS)}\n".encode("utf-8"))
            
            # Recebe as respostas dos jogadores.
            data = conn.recv(4096).decode("utf-8")

            # Formata respostas recebidas, com o nome do jogador, endereço,
            #horário que a mensagem foi recebida e o texto da mensagem.
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
            # Libera o acessoa à lista de respostas.
            SEMAFORO_RESPOSTAS.release()
            
            # A thread para e só continua se todos responderam
            SEMAFORO_TODOS_RESPONDERAM.acquire()

            # Faz o cálculo da pontuação e manda para todos.
            if nome == CLIENTES[0]["nome"]:
                calcular_pontos()
                enviar_pontuacoes()
            
            # Threads esperam para ninguém avançar sem que o cálculo tenha terminado.
            SEMAFORO_TODOS_RESPONDERAM.acquire()

# Cria a função que soma os pontos dos jogadores.
def calcular_pontos():
    global RESPOSTAS

    # Percorre cada tema.
    for i in range(len(TEMAS)):
        # Pega as respostas dos jogadores.
        respostas_coluna = [r[1][i].strip().lower() for r in RESPOSTAS]
        
        # Percorre cada jogador.
        for nome, respostas in RESPOSTAS:
            # Pega a reposta do jogador na categoria específica.
            resposta = respostas[i].strip().lower()
            # Verifica se a resposta é unica - se for recebe 3 pontos, senão recebe 1 ponto.    
            if respostas_coluna.count(resposta) == 1:
                PONTUACOES[nome] += 3
            else:
                PONTUACOES[nome] += 1

    # Inicia as respostas para a próxima rodada.
    RESPOSTAS = []

# Cria a função que envia as pontuações aos jogadores.
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

# Cria a função que estabelece as conexões.
def iniciar_servidor():
    # Cria a conexão, que termina quando o socket é fechado.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Tenta estabelecer a conexão na porta definida.
        s.bind((HOST, PORTA))
        s.listen()
        print("Servidor está aguardando jogadores")

        # Mantém o servidor rodando.
        while True:
            # Aceita pedidos de conexão.
            conn, addr = s.accept() 
            # Cria uma thread para atender o cliente conectado.
            threading.Thread(target=atender_cliente, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    iniciar_servidor()
