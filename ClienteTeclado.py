import socket
import time

HOST = "127.0.0.1" 
PORT = 9002

# Cria a função para estabelecer uma conexão com o servidor.
def conectar_servidor():

    # Tenta estabelecer uma conexão até dar certo.
    while True:
        try:
            # Cria o socket.
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Tenta a conexão no host e porta definidos.
            s.connect((HOST, PORT))
            print(" Conectado ao servidor!")
            
            # Recebe "Digite seu Nickname".
            pergunta = s.recv(1024).decode("utf-8")
            # Exibe a mensagem e espera a resposta do usuário.
            nick = input(pergunta)
            # Envia o nickname para o servidor.
            s.sendall(nick.encode("utf-8"))

            # Retorna a conexão pronta.
            return s
        
        # Tratamento de exceções - se o servidor não estiver ligado, espera 2 segundos e tenta a conexão de novo,
        #qualquer outro erro exibe uma mensagem mostrando qual foi o erro ocorrdo.
        except ConnectionRefusedError:
            print(" Aguardando servidor... Tentando novamente em 2 segundos")
            time.sleep(2)
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            time.sleep(2)

# Cria a função para o envio de mensagens .
def main():
    
    # Executa a função que conecta com o servidor.
    socket_cliente = conectar_servidor()
    print("Digite suas mensagens (ou sair para encerrar):")
    # Enquanto estiver ativo, permite envio de mensagens continuamente.
    while True:
        try:
            # Espera o usuário digitar.
            mensagem = input("_")
            # Se digitar "sair" a conexão é encerrada.
            if mensagem.lower() == 'sair': break
            # Se for vazio ele ignora e continua.
            if not mensagem.strip(): continue
            # Envia a mensage para o servidor.
            socket_cliente.sendall(mensagem.encode("utf-8"))
            
            # Recebe a confirmação do envio da mensagem.
            confirmacao = socket_cliente.recv(1024)
            
        # Tratamento de exceções - se a conexão caiu de forma abrupta ele termina a conexão e tenta reconectar,
        #qualquer outro erro ele informa qual foi o erro ocorrido e encerra o loop.
        except (BrokenPipeError, ConnectionResetError):
            print(" Conexão perdida. Tentando reconectar...")
            socket_cliente.close()
            socket_cliente = conectar_servidor()
        except Exception as e:
            print(f"Erro: {e}")
            break

    # Fecha a conexão. 
    socket_cliente.close()

if __name__ == "__main__":
    main()