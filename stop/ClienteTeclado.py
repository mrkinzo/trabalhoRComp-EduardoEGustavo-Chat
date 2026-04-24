import socket

HOST = "127.0.0.1"
PORT = 9002

# Cria a função que tenta estabelecer uma conexão com o servidor.
def main():

    # Cria a conexão, que termina quando o socket é fechado. 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Tenta se conectar ao servidor.
        s.connect((HOST, PORT))

        # Recebe a mensagem para enviar o nome do servidor.
        pergunta = s.recv(1024).decode("utf-8")
        # Exibe a pergunta e espera o usuário digitar.
        nome = input(pergunta)
        # Envia o nome para o servidor.
        s.sendall(nome.encode("utf-8"))

        # Mantém o cliante rodando.
        while True:
            # Espera o servidor mandar uma mensagem
            data = s.recv(4096)
            # Se não vier nada, o loop para.
            if not data:
                break

            # Recebe a mensagem do servidor e mostra na tela.
            msg = data.decode("utf-8")           
            print(msg)
            
            # Verifica se os temas da rodada foram definidos.
            if "TEMAS" in msg:
                # Aguarda as respostas do usuário e as envia para o servidor.
                respostas = input("Digite suas respostas: ")
                s.sendall(respostas.encode("utf-8"))

if __name__ == "__main__":
    main()
