#CLIENTE TELA para monitorar o envio das mensagens dos clientes, que são repassadas pelo servidor
import socket

HOST = "127.0.0.1"
PORT = 9003

def iniciar_tela():
    try:
        #cria a conexão, quando ela terminar o socket é fechado
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            #conecta ao servidor
            s.connect((HOST, PORT))
            print(f"[*] Monitorando mensagens em {HOST}:{PORT}...")
            #sempre tenta escutar mensagens
            while True:
                #espera o servidor enviar algo, e quando enviado, guarda na variável "data"
                data = s.recv(4096) 
                #se o servidor terminou a conexão ele sai do loop
                if not data:
                    print("\n[!] Servidor desconectado.")
                    break
                
                # mostra a mensagem recebida do servidor - "decode" para transformar em texto, "strip" para remover espaços
                print(f"\n{data.decode('utf-8').strip()}")
    #se o servidor não estiver ligado exibe uma mensagem de erro
    except ConnectionRefusedError:
        print("[!] Erro: Servidor não está online.")
    #qualquer outro erro, envia uma mensagem com o erro que ocorreu
    except Exception as e:
        print(f"[!] Erro inesperado: {e}")

if __name__ == "__main__":
    iniciar_tela()