import struct
import asyncio

# Lista em memória para guardar as mensagens.
memory_messages = []

async def handle_client(reader, writer):
    try:
        data = await reader.readexactly(3)
        payload_size, operacao = struct.unpack("!HB", data)

        if operacao == 0x00:  # Operação de escrita
            if payload_size > 0:
                payload_data = await reader.readexactly(payload_size)
                message = payload_data.decode('utf-8')
                memory_messages.append(message)

                print(f"[Operação 0x00] Mensagem armazenada em memória: {message}")

        elif operacao == 0x01:  # Operação de leitura
            if memory_messages:
                response_message = memory_messages.pop(0)
                rsp_msg_bytes = response_message.encode('utf-8')

                print(f"[Operação 0x01] Mensagem lida da memória: {response_message}")

                header_response = struct.pack("!HB", len(rsp_msg_bytes), 0x01)
                writer.write(header_response + rsp_msg_bytes)
                await writer.drain()

                print(f"[Operação 0x01] Mensagem enviada ao cliente: {response_message}")
            else:
                print("[Operação 0x01] Nenhuma mensagem disponível para leitura.")

                response_data = struct.pack("!HB", 0, 0x01)  # Resposta vazia
                writer.write(response_data)
                await writer.drain()

                print("[Operação 0x01] Resposta vazia enviada ao cliente.")

    except asyncio.IncompleteReadError:
        print("Erro: Conexão fechada pelo cliente antes de enviar todos os bytes prometidos.")

    except Exception as e:
        print(f"Erro ao lidar com o cliente: {e}")

    finally:
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, '0.0.0.0', 8080)
    print("Servidor rodando em 0.0.0.0:8080...")
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())