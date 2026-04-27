import socket

HOST = "127.0.0.1"
PORT = 9003


# Cria a função que permite o cliente receber as mensagens enviadas.
def iniciar_tela():

    try:
        # Cria a conexão, que termina quando o socket é fechado.
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Tenta a conexão com o host e pora definidos.
            s.connect((HOST, PORT))
            print(f"[*] Monitorando mensagens em {HOST}:{PORT}...")
            # Sempre tenta escutar mensagens.
            while True:
                # Espera por mensagens do servidor, e quando enviado, guarda na variável "data".
                data = s.recv(4096)
                # Se o servidor terminou a conexão ele sai do loop.
                if not data:
                    print("\n[!] Servidor desconectado.")
                    break

                # Mostra a mensagem recebida do servidor,
                # "decode" para transformar em texto, "strip" para remover espaços.
                print(f"\n{data.decode('utf-8').strip()}")

    # Tratamento de exceções - se o servidor recusou a conexão, exibe uma mensagem alertando o usuário,
    # qualquer outro erro ele exibe o erro real o
    except ConnectionRefusedError:
        print("[!] Erro: Servidor não está online.")
    except Exception as e:
        print(f"[!] Erro inesperado: {e}")


if __name__ == "__main__":
    iniciar_tela()
