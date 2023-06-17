import socket
import logging
import struct

class Hman:
    """Class to communicate with the hman.
    
    Attributes:
        nb_mot (int): Number of motors.
        verbose (bool): Verbose mode.
        mode (str): Current mode.
        modes (dict): Dictionary of possible modes.
        positions (list): List of encoder positions.
        target_positions (list): List of target positions.
        target_currents (list): List of target currents.
        port (int): Port of the hman.
        address (str): IP address of the hman.
    """
    def __init__(self, nb_mot, verbose):
        self.nb_mot = nb_mot
        self.verbose = verbose
        self._pkgSize = 2 + nb_mot * 8
        self.mode = None
        self._cmd = bytearray(self._pkgSize)
        self._client = None
        self.positions = [0, 0, 0]#encoder positions
        self.target_positions = [0, 0, 0]
        self.target_currents = [0, 0, 0]

        self.port = 5000
        self.address = 'localhost'

        #enum of possible modes
        self.modes = {
            'position': 0,
            'current': 1,
            'velocity': 2,
            'impedance': 3
        }

        logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
        logging.info('Initialised.')

    def __del__(self):
        """Destructor."""
        self.disconnect()
        logging.info('Disconnected.')
    
    def disconnect(self):
        """Disconnect from the hman."""
        self.turn_off_current()
        if self._client:
            self._client.close()
        logging.info('Disconnected.')

    def connect(self, address, port=5000):
        """Connect to the hman.
        Args:
            address (str): IP address of the hman. the port is fixed to 5000.
        """
        self.address = address
        self.port = port
        logging.info('Connecting to %s:%d...', self.address, self.port)
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self._client.connect((address, self.HMAN_PORT))
        except socket.error as exc:
            logging.error(f'Caught exception socket.error : {exc}')

    def set_mode(self, mode):
        """Set the mode of the hman.
        Args:
            mode (str): Mode to set.
        """
        if mode not in self.modes:#check if the mode is valid
            logging.error('Invalid mode.')
            return
        logging.info('Setting mode to %s', mode)
        self.mode = mode
        self._cmd[0] = ord('M')
        self._cmd[2:6] = struct.pack('>i', self.modes[mode])
        self._client.sendall(self._cmd)

    def __set_values(self, val, n):
        """Set the values of the hman.
        Args:
            val (list): List of values to set.
            n (int): Number of values to set.
        Returns:
            list: List of encoder positions.
        """
        self._cmd[0] = ord('V')
        self._cmd[1] = self.nb_mot
        logging.debug('Setting values to %s', val)

        for i in range(n):
            self._cmd[2 + i * 4 : 2 + (i + 1) * 4] = struct.pack('>i', val[i])
        self._client.sendall(self._cmd)
        # wait for the response
        data = self._client.recv(self.nb_mot * 4)
        if not data:
            logging.error('No data received.')
            return
        self.positions = [struct.unpack('>i', data[i*4 : (i+1)*4])[0] for i in range(self.nb_mot)]#encoder positions
        return self.positions
        

    def set_cartesian_pos(self, posx, posy, posz):
        """Set the cartesian position of the hman.
        Args:
            posx (float): X position.
            posy (float): Y position.
            posz (float): Z position.
        Returns:
            list: List of encoder positions.
        """
        if self.mode != 'position':
            self.set_mode('position')

        pos = [-posx + posy, -posx - posy, posz]
        self.target_positions = pos
        self.__set_values(pos, 3)
        #transform the cartesian articular position to cartesian position
        return [(self.positions[0] + self.positions[1]) / 2, (-self.positions[0] + self.positions[1]) / 2, self.positions[2]]

    def set_articular_pos(self, pos1, pos2, pos3):
        """Set the articular position of the hman.
        Args:
            pos1 (float): Position of the first motor.
            pos2 (float): Position of the second motor.
            pos3 (float): Position of the third motor.
        Returns:
            list: List of encoder positions.
        """ 
        if self.mode != 'position':
            self.set_mode('position')

        pos = [pos1, pos2, pos3]
        self.target_positions = pos
        self.__set_values(pos, 3)
        return self.positions

    def set_motors_current(self, cur1, cur2, cur3):
        """Set the current of the motors.
        Args:
            cur1 (float): Current of the first motor.
            cur2 (float): Current of the second motor.
            cur3 (float): Current of the third motor.
        Returns:
            list: List of encoder positions.
        """
        if self.mode != 'current':
            self.set_mode('current')

        curr = [cur1, cur2, cur3]
        self.target_currents = curr
        self.__set_values(curr, 3)
        return self.positions

    def turn_off_current(self):
        """Turn off the current of the motors.
        """
        if self.mode != 'current':
            self.set_mode('current')

        cur = [0] * self.nb_mot
        self.__set_values(cur, self.nb_mot)

    def get_pos(self):
        """Get the position of the motors.
        Returns:
            list: List of encoder positions.
        """
        self._cmd[0] = ord('P')
        self._cmd[1] = self.nb_mot
        self._client.sendall(self._cmd)

        response = self._client.recv(self.nb_mot * 4)
        self.positions = [struct.unpack('>i', response[i*4 : (i+1)*4])[0] for i in range(self.nb_mot)]#encoder positions
        return self.positions

if __name__ == '__main__':
    #create a hman object
    hman = Hman(3, True)
    #connect to the hman
    hman.connect('127.0.0.1')
    #set the motors in position mode
    hman.set_mode('position')
    #set the motors in articular position
    pos = hman.set_articular_pos(0, 40, 30)
    print(pos)