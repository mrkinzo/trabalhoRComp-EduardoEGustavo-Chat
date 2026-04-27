import threading
from time import sleep
import socket
from datetime import datetime

# Aceita conexões de qualquer lugar.
<<<<<<<< HEAD:mensagens-grupo/Server.py
HOST = "0.0.0.0"
# Porta para conexão com o produtor.
PORTA_ENTRADA = 9002
# Porta para conexão com o consumidor.
PORTA_SAIDA = 9003  #
========
HOST = "0.0.0.0" 
# Porta para conexão com o produtor.
PORTA_ENTRADA = 9002  
# Porta para conexão com o consumidor.
PORTA_SAIDA = 9003    #
>>>>>>>> eba53b352f22af5adc14d334b28d0a71fa586828:trabalho_redes/mensagens-grupo/Server.py

# Cria uma lista que guarda as mensagens recebidas do produtor.
FILA = []
# Cria uma lista dos consumidores conectados para receber mensagens.
CLIENTES_TELA = []

# Cria um semáforo que controla o acesso à fila - definindo 1 thread por vez.
<<<<<<<< HEAD:mensagens-grupo/Server.py
SEMAFORO_ACESSO_FILA = threading.Semaphore(1)
# Cria um semáforo que controla o número de itens disponiveis na lista - inicializando com 0.
SEMAFORO_ITENS_FILA = threading.Semaphore(0)
# Cria um semáforo que controla o acesso à lista de clientes - definindo 1 thread por vez.
SEMAFORO_CLIENTES = threading.Semaphore(1)
========
SEMAFORO_ACESSO_FILA = threading.Semaphore(1) 
# Cria um semáforo que controla o número de itens disponiveis na lista - inicializando com 0.
SEMAFORO_ITENS_FILA = threading.Semaphore(0)  
# Cria um semáforo que controla o acesso à lista de clientes - definindo 1 thread por vez.
SEMAFORO_CLIENTES = threading.Semaphore(1)    
>>>>>>>> eba53b352f22af5adc14d334b28d0a71fa586828:trabalho_redes/mensagens-grupo/Server.py

# Cria a função que coloca as mensagens na fila.
def produzir(mensagem):

    # Indica que a a fila será utilizada.
    SEMAFORO_ACESSO_FILA.acquire()
    # Adiciona a mensagem na fila.
    FILA.append(mensagem)
    print(f"[LOG] Nova mensagem na fila.")
    # Libera a fila para ser usada novamente.
    SEMAFORO_ACESSO_FILA.release()
    # Adiciona um novo item na lista.
    SEMAFORO_ITENS_FILA.release()
<<<<<<<< HEAD:mensagens-grupo/Server.py


========
    
>>>>>>>> eba53b352f22af5adc14d334b28d0a71fa586828:trabalho_redes/mensagens-grupo/Server.py
# Cria a função que tira as mensagens da fila.
def consumir():

    # Tenta retirar um item da lista.
    SEMAFORO_ITENS_FILA.acquire()
    SEMAFORO_ACESSO_FILA.acquire()
    # Captura a primeira mensagem da fila, se houver itens.
    mensagem = FILA.pop(0) if FILA else None
    # Libera a fila
    SEMAFORO_ACESSO_FILA.release()
    # Devolve a mensagem.
    return mensagem

<<<<<<<< HEAD:mensagens-grupo/Server.py

# Cria a função que aceita conexões dos produtores.
def escutar_teclado():

    # Cria a conexão, que termina quando o socket é fechado.
========
# Cria a função que escuta clientes.
def escutar_teclado():

  # Cria a conexão, que termina quando o socket é fechado.
>>>>>>>> eba53b352f22af5adc14d334b28d0a71fa586828:trabalho_redes/mensagens-grupo/Server.py
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Permite reutilizar a porta.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Conecta o servidor na porta 9002.
        s.bind((HOST, PORTA_ENTRADA))
        # Começa a escutar conexões.
        s.listen()
<<<<<<<< HEAD:mensagens-grupo/Server.py
        print(f"[*] Aguardando Produtores na porta {PORTA_ENTRADA}...")

        while True:
            # Se alguém conectou, aceita a conexão.
            conn, addr = s.accept()
            # Criar uma thread para cada teclado que permite múltiplos digitadores.
            threading.Thread(
                target=atender_produtor, args=(conn, addr), daemon=True
            ).start()

========
        print(f"[*] Aguardando Teclados na porta {PORTA_ENTRADA}...")
    
        while True:
            # Se alguém conectou, aceita a conexão.
            conn, addr = s.accept()
            # Cria uma thread para cada teclado que permite múltiplos digitadores.
            threading.Thread(target=atender_produtor, args=(conn, addr), daemon=True).start()
>>>>>>>> eba53b352f22af5adc14d334b28d0a71fa586828:trabalho_redes/mensagens-grupo/Server.py

# Cria a função que atende o produtor.
def atender_produtor(conn, addr):

    # Com a conexão estabelecida...
    with conn:
        try:
<<<<<<<< HEAD:mensagens-grupo/Server.py
            # Solicita o nickname do produtor
            conn.sendall("Digite seu Nickname: ".encode("utf-8"))
            # Recebe o nickname
            nickname = conn.recv(1024).decode("utf-8").strip() or "Anon"

            while True:
                # Guarda as mensagens recebidas
                data = conn.recv(1024)
                # Se o cliente saiu, encerra a conexão
                if not data:
                    break

                # Formatação das mensagens - pega a hora atual e monta a mensagem com o nickname,
                # endereço IP do cliente, horário e o texto da mensagem.
                horario = datetime.now().strftime("%H:%M:%S")
                msg_formatada = (
                    f"[{nickname} ({addr[0]}) {horario}]: {data.decode('utf-8')}"
                )
========
            # Solicita o nickname do produtor.
            conn.sendall("Digite seu Nickname: ".encode("utf-8"))
            # Recebe o nickname.
            nickname = conn.recv(1024).decode("utf-8").strip() or "Anon"

            while True:
                # Guarda as mensagens recebidas.
                data = conn.recv(1024)
                # Se o cliente saiu, encerra a conexão.
                if not data: break
                
                # Formatação das mensagens - pega a hora atual e monta a mensagem com o nickname,
                #endereço do cliente, horário e o texto da mensagem.
                horario = datetime.now().strftime("%H:%M:%S")
                msg_formatada = f"[{nickname} ({addr[0]}) {horario}]: {data.decode('utf-8')}"
>>>>>>>> eba53b352f22af5adc14d334b28d0a71fa586828:trabalho_redes/mensagens-grupo/Server.py
                # Coloca a mensagem formatada na fila.
                produzir(msg_formatada)
                # Responde para o cliente que a mensagem foi recebida.
                conn.sendall(b"OK\n")

                # Tratamento de exceções - qualquer erro que ocorrer é exibido sua causa.
        except Exception as e:
            print(f"Erro com produtor {addr}: {e}")

<<<<<<<< HEAD:mensagens-grupo/Server.py

========
>>>>>>>> eba53b352f22af5adc14d334b28d0a71fa586828:trabalho_redes/mensagens-grupo/Server.py
# Cria a função que gerencia as telas
def gerenciar_telas():

    # Cria a conexão, que termina quando o socket é fechado.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Permite reutilizar a porta.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Abre o servidor na porta 9003
        s.bind((HOST, PORTA_SAIDA))
        s.listen()
        print(f"[*] Aguardando Telas na porta {PORTA_SAIDA}...")
<<<<<<<< HEAD:mensagens-grupo/Server.py

        while True:
            # Aceita conexões do consumidor
========
        
        while True:
            # Aceita conexões do consumidor.
>>>>>>>> eba53b352f22af5adc14d334b28d0a71fa586828:trabalho_redes/mensagens-grupo/Server.py
            conn, addr = s.accept()
            # Indica que um cliente se conectou.
            SEMAFORO_CLIENTES.acquire()
            # Adiciona na lista.
            CLIENTES_TELA.append(conn)
            # Tira a conexão da lista.
            SEMAFORO_CLIENTES.release()
            print(f"[+] Tela conectada: {addr}")

<<<<<<<< HEAD:mensagens-grupo/Server.py

# Cria a função que envia as mensagens para todos os clientes conectados.
========
  # Cria a função que envia as mensagens para todos os clientes conectados.
>>>>>>>> eba53b352f22af5adc14d334b28d0a71fa586828:trabalho_redes/mensagens-grupo/Server.py
def thread_distribuidora():

    while True:
        # Obtém a mensagem da fila.
        msg = consumir()

<<<<<<<< HEAD:mensagens-grupo/Server.py
        if not msg:
            continue
        # Pega um cliente da fila.
        SEMAFORO_CLIENTES.acquire()
        # Percorre todos os clientes conectados.
        for cliente in list(CLIENTES_TELA): # list para evitar a modificação da lista durante a iteração.
========
        if not msg: continue
        # Pega um cliente da fila.
        SEMAFORO_CLIENTES.acquire()
        # Percorre todos os clientes conectados.
        for cliente in list(CLIENTES_TELA):
>>>>>>>> eba53b352f22af5adc14d334b28d0a71fa586828:trabalho_redes/mensagens-grupo/Server.py
            # Tenta enviar a mensagem criptografada para o cliente.
            try:
                cliente.sendall(f"{msg}\n".encode("utf-8"))
            # Se o cliente terminou a conexão, ele é removido da fila
            except:
                CLIENTES_TELA.remove(cliente)
                cliente.close()
        SEMAFORO_CLIENTES.release()

<<<<<<<< HEAD:mensagens-grupo/Server.py

# Cria a função que cria as threads e as inicia.
========
# Cria a função que cria as threads e as inicia.

>>>>>>>> eba53b352f22af5adc14d334b28d0a71fa586828:trabalho_redes/mensagens-grupo/Server.py
def main():

    # Thread para escutar quem envia dados.
    t1 = threading.Thread(target=escutar_teclado, daemon=True)
    # Thread para gerenciar conexões de quem recebe dados.
    t2 = threading.Thread(target=gerenciar_telas, daemon=True)
    # Thread que consome a fila e faz o broadcast (envio para todos).
    t3 = threading.Thread(target=thread_distribuidora, daemon=True)

    # Inicia todas as threads ao mesmo tempo.
    t1.start()
    t2.start()
    t3.start()
<<<<<<<< HEAD:mensagens-grupo/Server.py

    try:
        # Mantém o servidor rodando.
        t1.join()
    except KeyboardInterrupt:
        print("\nServidor finalizado.")


========
    
    try:
        # Mantém o servidor rodando.
        t1.join() 
    except KeyboardInterrupt:
        print("\nServidor finalizado.")

>>>>>>>> eba53b352f22af5adc14d334b28d0a71fa586828:trabalho_redes/mensagens-grupo/Server.py
if __name__ == "__main__":
    main()
