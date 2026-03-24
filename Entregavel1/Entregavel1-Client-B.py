import struct
import socket

# Monta o cabeçalho de RECUPERAR: Tamanho 0, Operação 0x01
header = struct.pack("!HB", 0, 0x01)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('127.0.0.1', 8080))
    s.sendall(header) # Envia a solicitação

    # Aguarda a resposta do servidor lendo os 3 bytes de cabeçalho
    header_resp = s.recv(3)

    if len(header_resp) == 3:
        payload_size, operacao = struct.unpack("!HB", header_resp)

        if payload_size > 0:
            # Lê o payload garantindo o tamanho exato prometido pelo servidor
            msg_bytes = s.recv(payload_size)
            print(f"Mensagem recebida do servidor: {msg_bytes.decode('utf-8')}")
        else:
            print("Nenhuma mensagem armazenada no servidor.")