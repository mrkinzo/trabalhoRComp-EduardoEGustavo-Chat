import threading
from time import sleep
import socket
from datetime import datetime

#aceita conexão de qualquer lugar
HOST = "0.0.0.0" 
#porta para conexão com o cliente produtor
PORTA_ENTRADA = 9002  
#porta para conexão com o cliente consumidor
PORTA_SAIDA = 9003    #

#lista que guarda as mensagens recebidas do produtor
FILA = []
#lista dos consumidores conectados para receber mensagens
CLIENTES_TELA = []

#               <=SEMÁFOROS=>
# garante que só 1 thread por vez pode mexer na fila
SEMAFORO_ACESSO_FILA = threading.Semaphore(1) 
# contador dos itens disponíveis na fila, incializando com 0
SEMAFORO_ITENS_FILA = threading.Semaphore(0)  
# protege a lista dos consumidores
SEMAFORO_CLIENTES = threading.Semaphore(1)    

#           <=PRODUÇÃO DA MENSAGEM=>
def produzir(mensagem):
    #indica que a a fila será utilizada
    SEMAFORO_ACESSO_FILA.acquire()
    #adiciona a mensagem na fila
    FILA.append(mensagem)
    print(f"[LOG] Nova mensagem na fila.")
    #libera a fila para poder ser usada novamente
    SEMAFORO_ACESSO_FILA.release()
    #informa que tem um novo item disponivel na lista
    SEMAFORO_ITENS_FILA.release()
    
#           <=CONSUMO DA MENSAGEM=>
def consumir():
    #tenta retirar um item da fila, se não houver, espera
    SEMAFORO_ITENS_FILA.acquire()
    SEMAFORO_ACESSO_FILA.acquire()
    #captura a primeira mensagem da fila
    mensagem = FILA.pop(0) if FILA else None
    #libera a fila
    SEMAFORO_ACESSO_FILA.release()
    #devolve a mensagem
    return mensagem

#           <=TRATAMENTO DE ENTRADA (PRODUTOR)=>
def escutar_teclado():
  #  cria a conexão na porta do produtor
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
        s.bind((HOST, PORTA_ENTRADA))
        #começa a escutar conexões
        s.listen()
        print(f"[*] Aguardando Teclados na porta {PORTA_ENTRADA}...")
    
        while True:
            #se alguém conectou, aceita a conexão
            conn, addr = s.accept()
            # criar uma thread para cada teclado que permite múltiplos digitadores
            threading.Thread(target=atender_produtor, args=(conn, addr), daemon=True).start()

def atender_produtor(conn, addr):
    with conn:
        try:
            # solicita o nickname do produtor
            conn.sendall("Digite seu Nickname: ".encode("utf-8"))
            # recebe o nickname
            nickname = conn.recv(1024).decode("utf-8").strip() or "Anon"
            #ouve mensagens 
            while True:
                #guarda as mensagens recebidas
                data = conn.recv(1024)
                #se o cliente saiu, encerra a conexão
                if not data: break
                
                # formatação das mensagens
                horario = datetime.now().strftime("%H:%M:%S")
                msg_formatada = f"[{nickname} ({addr[0]}) {horario}]: {data.decode('utf-8')}"
                #coloca a mensagem formatada na fila
                produzir(msg_formatada)
                #respondi para o cliente que a mensagem foi recebida
                conn.sendall(b"OK\n")
                #qualquer exceção que ocorrer ele exibe uma mensagem que mostra o erro
        except Exception as e:
            print(f"Erro com produtor {addr}: {e}")

#           <=TRATAMENTO DE SAÍDA (CONSUMIDOR)=>
def gerenciar_telas():
    # abre o servidor na porta do consumidor e aguarda conexões
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORTA_SAIDA))
        s.listen()
        print(f"[*] Aguardando Telas na porta {PORTA_SAIDA}...")
        
        while True:
            # produto conecetou
            conn, addr = s.accept()
            # indica que um cliente se conectou
            SEMAFORO_CLIENTES.acquire()
            # adiciona na lista
            CLIENTES_TELA.append(conn)
            # tira a conexão da lista
            SEMAFORO_CLIENTES.release()
            print(f"[+] Tela conectada: {addr}")

  #  Múltiplos consumidores: ela retira as mensagens da fila e entrega para todos os clientes conectados na lista CLIENTES_TELA.
def thread_distribuidora():
    while True:
        # pega a mensagem da fila
        msg = consumir()

        if not msg: continue
        # pega um cliente da fila
        SEMAFORO_CLIENTES.acquire()
        # percorre todos os clientes conectados
        for cliente in list(CLIENTES_TELA):
            try:
                #envia a mensagem criptografada para o cliente
                cliente.sendall(f"{msg}\n".encode("utf-8"))
            except:
                # remove quem desconectou
                CLIENTES_TELA.remove(cliente)
                cliente.close()
        SEMAFORO_CLIENTES.release()

# --- INICIALIZAÇÃO ---

def main():
    # Thread para escutar quem envia dados
    t1 = threading.Thread(target=escutar_teclado, daemon=True)
    # Thread para gerenciar conexões de quem recebe dados
    t2 = threading.Thread(target=gerenciar_telas, daemon=True)
    # Thread que consome a fila e faz o broadcast (envio para todos)
    t3 = threading.Thread(target=thread_distribuidora, daemon=True)
    
    # inicia todas as threads ao mesmo tempo
    t1.start()
    t2.start()
    t3.start()
    
    try:
        t1.join() # Mantém o servidor rodando
    except KeyboardInterrupt:
        print("\nServidor finalizado.")

if __name__ == "__main__":
    main()