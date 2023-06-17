import socket
import threading
import struct
import logging

class HmanServer:
    def __init__(self, host='localhost', port=5000, verbose=False):
        self.host = host
        self.port = port
        self.pkgSize = 2 + 8*3
        self.positions = [0, 0, 0]#encoder positions
        self.target_positions = [0, 0, 0]
        self.target_currents = [0, 0, 0]#
        self.modes = 0
        self.data = bytearray(3*4)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(1)
        logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
        logging.info('Server started at {self.host}:{self.port}')

    def start(self):
        while True:
            logging.info('Waiting for a connection on port {host}:{port}...'.format(host=self.host, port=self.port))
            client, addr = self.server.accept()

            logging.info('Connected by {addr}'.format(addr=addr))
            threading.Thread(target=self.handle_client, args=(client,)).start()
    
    def set_positions(self, positions):
        self.positions = positions

    def handle_client(self, client):
        while True:
            # Check if there's enough data to read
            data = client.recv(self.pkgSize)
            if not data:
                break
            logging.debug('Received {n} bytes: {data}'.format(n=len(data), data=data))
            cmd = data[0]
            index = data[1]
            logging.info('Cmd: {cmd} | Index: {index}'.format(cmd=chr(cmd), index=index))

            if cmd == ord('M'):  # mode
                mode = struct.unpack('>i', data[2:6])[0]
                logging.info('Setting mode to {mode}...'.format(mode=mode))

            elif cmd == ord('V'):  # set value
                values = [struct.unpack('>i', data[i:i+4])[0] for i in range(2, 4*index, 4)]
                logging.info('Setting values to {values}'.format(values=values))
                if mode == 0:
                    self.target_positions = values
                elif mode == 1:
                    self.target_currents = values
                for i in range(3):
                    self.data[4*i:4*(i+1)] = struct.pack('>i', self.positions[i])
                    print(self.data[4*i:4*(i+1)])
                client.sendall(self.data)
                

            elif cmd == ord('P'):  # return encoder position
                # send back the position
                for i in range(3):
                    self.data[4*i:4*(i+1)] = struct.pack('>i', self.positions[i])
                client.sendall(self.data)

        client.close()
        print('Connection closed')

if __name__ == '__main__':
    server = HmanServer()
    server.set_positions([1, 2, 3])
    server.start()
