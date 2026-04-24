
import socket
import time

#localhost
HOST = "127.0.0.1" 
#porta para comunicar
PORT = 9002

#função para conectar ao servidor
def conectar_servidor():
    #tenta conectar até dar certo
    while True:
        try:
            #criando o socket, o canal de comunicação
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #tenta a conexão no host e port definidos
            s.connect((HOST, PORT))
            #só aparece se a conexão funcionou
            print(" Conectado ao servidor!")
            
            #recebe "Digite seu Nickname" e converte de bytes para texto
            pergunta = s.recv(1024).decode("utf-8")
            #mostra a pergunta para o usuário e espera a resposta
            nick = input(pergunta)
            #envia o nickname para o servidor
            s.sendall(nick.encode("utf-8"))

            #retorna a conexão pronta 
            return s
        #se o servidor não estiver ligado, espera 2 segundos para tentar conectar novamente
        except ConnectionRefusedError:
            print(" Aguardando servidor... Tentando novamente em 2 segundos")
            time.sleep(2)
        #se houver qualquer outro erro, ele também espera 2 segundo para conectar novamente
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            time.sleep(2)

#função principal 
def main():
    #executa a função que faz a conexão com o servidor
    socket_cliente = conectar_servidor()
    #mostra as instruções
    print("Digite suas mensagens (ou 'sair' para encerrar):")
    #enquanto ele estiver ativo, permite envio de mensagens continuamente
    while True:
        try:
            #espera o usuário digitar
            mensagem = input("_")
            #se digitar sair, ele encerra
            if mensagem.lower() == 'sair': break
            #se for vazia ele ignora
            if not mensagem.strip(): continue
            #envia a mensagem ao servidor
            socket_cliente.sendall(mensagem.encode("utf-8"))
            
            #recebe a confirmação do envio da mensagem pelo servidor
            confirmacao = socket_cliente.recv(1024)
            
        #se a conexão cair, fecha a atual e tenta conectar de novo
        except (BrokenPipeError, ConnectionResetError):
            print(" Conexão perdida. Tentando reconectar...")
            socket_cliente.close()
            socket_cliente = conectar_servidor()
        #se ocorrer qualquer outra exceção ele mostra o erro e encerra o loop
        except Exception as e:
            print(f"Erro: {e}")
            break
    #fecha a conexão 
    socket_cliente.close()

if __name__ == "__main__":
    main()