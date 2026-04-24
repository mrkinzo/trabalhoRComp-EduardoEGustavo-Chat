import threading
from time import sleep
import socket
from datetime import datetime

# --- CONFIGURAÇÕES ---
HOST = "0.0.0.0"#Escuta em todas as interfaces de rede
PORTA_ENTRADA = 9002  # Porta para os produtores (Teclado)
PORTA_SAIDA = 9003    # Porta para os consumidores (Tela)

# Fila e Lista de Clientes
FILA = []
CLIENTES_TELA = []

# --- SEMÁFOROS ---
# Protege o acesso à lista FILA
SEMAFORO_ACESSO_FILA = threading.Semaphore(1) 
# Contador de itens para os consumidores
SEMAFORO_ITENS_FILA = threading.Semaphore(0)  
# Protege a lista de conexões de saída
SEMAFORO_CLIENTES = threading.Semaphore(1)    

# --- LÓGICA DE PRODUÇÃO E CONSUMO ---

def produzir(mensagem):
    #Adiciona mensagens formatadas à fila compartilhada
    SEMAFORO_ACESSO_FILA.acquire()
    FILA.append(mensagem)
    print(f"[LOG] Nova mensagem na fila.")
    SEMAFORO_ACESSO_FILA.release()
    SEMAFORO_ITENS_FILA.release()

def consumir():
    #Retira um item da fila. Bloqueia se a fila estiver vazia.
    SEMAFORO_ITENS_FILA.acquire()
    SEMAFORO_ACESSO_FILA.acquire()
    mensagem = FILA.pop(0) if FILA else None
    SEMAFORO_ACESSO_FILA.release()
    return mensagem

# --- TRATAMENTO DE ENTRADA (TECLADO / PRODUTOR) ---

def escutar_teclado():
  #  Monitora a porta 9002 para novos produtores
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #re usa a porta imediatamente após o fechamento
        s.bind((HOST, PORTA_ENTRADA))
        s.listen()
        print(f"[*] Aguardando Teclados na porta {PORTA_ENTRADA}...")
        
        while True:
            conn, addr = s.accept()
            # Criar uma thread para cada teclado permite múltiplos digitadores
            threading.Thread(target=atender_produtor, args=(conn, addr), daemon=True).start()

def atender_produtor(conn, addr):
    """Lida com o recebimento de mensagens e o Nickname de cada produtor."""
    with conn:
        try:
            # Solicita o Nickname assim que o cliente conecta
            conn.sendall("Digite seu Nickname: ".encode("utf-8"))
            nickname = conn.recv(1024).decode("utf-8").strip() or "Anon"
            
            while True:
                data = conn.recv(1024)
                if not data: break
                
                # Formatação das mensagens conforme o requisito
                horario = datetime.now().strftime("%H:%M:%S")
                msg_formatada = f"[{nickname} ({addr[0]}) {horario}]: {data.decode('utf-8')}"
                
                produzir(msg_formatada)
                conn.sendall(b"OK\n")
        except Exception as e:
            print(f"Erro com produtor {addr}: {e}")

# --- TRATAMENTO DE SAÍDA (TELA / CONSUMIDOR) ---

def gerenciar_telas():
    #Monitora a porta 9003 para novos consumidores (Telas).
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #re usa a porta imediatamente após o fechamento
        s.bind((HOST, PORTA_SAIDA))#vincula o socket à porta de saída
        s.listen()
        print(f"[*] Aguardando Telas na porta {PORTA_SAIDA}...")
        
        while True:
            conn, addr = s.accept()
            SEMAFORO_CLIENTES.acquire()
            CLIENTES_TELA.append(conn)
            SEMAFORO_CLIENTES.release()
            print(f"[+] Tela conectada: {addr}")

def thread_distribuidora():
   
  #  Esta é a função de múltiplos consumidores: ela retira da fila
   # e espalha para todos os clientes conectados na lista CLIENTES_TELA.
  
    while True:
        msg = consumir()
        if not msg: continue

        SEMAFORO_CLIENTES.acquire()
        # Enviamos para todos os clientes ativos
        for cliente in list(CLIENTES_TELA):
            try:
                cliente.sendall(f"{msg}\n".encode("utf-8"))
            except:
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
    
    t1.start()
    t2.start()
    t3.start()
    
    try:
        t1.join() # Mantém o servidor rodando
    except KeyboardInterrupt:
        print("\nServidor finalizado.")

if __name__ == "__main__":
    main()