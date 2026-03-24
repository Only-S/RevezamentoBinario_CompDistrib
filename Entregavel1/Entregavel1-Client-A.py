import struct
import socket

mensagem = "Olá, mundo!".encode('utf-8')
header = struct.pack("!HB", len(mensagem), 0x00) # ! = Network Order (Big-endian), H = 2 bytes, B = 1 byte
pacote_completo = header + mensagem

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect(('localhost', 8080))
    s.sendall(pacote_completo) # Envio de dados
    print("Mensagem enviada ao servidor!")