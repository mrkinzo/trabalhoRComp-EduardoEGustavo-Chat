import socket

HOST = "127.0.0.1"
PORT = 9002


# Cria a função que permite o cliente receber as mensagens enviadas.
def iniciar_tela():

    # Tenta criar a conexão, que termina quando o socket é fechado.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Tenta se conectar ao servidor.
            s.connect((HOST, PORT))

            # Recebe o pedido de enviar o nome.
            s.recv(1024)
            # Como o consumidor não envia nada, ele define "TELA" como o nome padrão para identificação.
            s.sendall("TELA".encode("utf-8"))

            while True:
                # Aguarda pelo envio de mensagens.
                data = s.recv(4096)
                # Se não vier mensagens, o loop para.
                if not data:
                    break
                # Se for recebido mensagens, elas são exibidas para o usuário.
                print(data.decode("utf-8"))

    # Tratamento de exceções - qualquer erro que ocorrer ele apenas exibe qual foi o erro.
    except Exception as e:
        print(e)


if __name__ == "__main__":
    iniciar_tela()
