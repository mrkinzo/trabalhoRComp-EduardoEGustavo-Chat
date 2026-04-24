import socket

HOST = "127.0.0.1"
PORT = 9003

def iniciar_tela():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print(f"[*] Monitorando mensagens em {HOST}:{PORT}...")
            
            while True:
                data = s.recv(4096) # Aumentado para suportar mensagens formatadas longas
                if not data:
                    print("\n[!] Servidor desconectado.")
                    break
                
                # Limpa a linha atual e imprime a mensagem formatada
                print(f"\n{data.decode('utf-8').strip()}")
                print("------------------------------------------", end="")
    except ConnectionRefusedError:
        print("[!] Erro: Servidor não está online.")
    except Exception as e:
        print(f"[!] Erro inesperado: {e}")

if __name__ == "__main__":
    iniciar_tela()