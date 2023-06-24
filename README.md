# pyHman
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is a Python library for controlling and communicating with the Hman device. This library provides high-level interfaces to set and get various parameters of hman, such as motor positions, modes, currents, and so on.

## Installation

This package uses setuptools for distribution. You can install it via pip:
```bash
pip install pyHman
```

or directly from the source code:

```bash
git clone https://github.com/Aightech/pyHman.git
cd pyHman
python setup.py install
```

### Requirements

- Python 3.6+
- **socket** (from the Python Standard Library)
- **logging** (from the Python Standard Library)


## Usage

```python
from Hman import Hman

# Create a Hman instance
hman = Hman(3, True) # '3' denotes the number of motors, 'True' enables verbose logging
# Connect to the hman
hman.connect('127.0.0.1') # Use the appropriate IP address for your setup
# Set the mode of the motors
hman.set_mode('position') # Other available modes: 'current', 'velocity', 'impedance'
# Set the articular position of the motors
positions = hman.set_articular_pos(0, 40, 30) # Enter the desired positions for each motor
# Print the positions
print(positions)
```

## Features and Functions

The Hman class provides the following main features:

- `connect(address: str, port: int = 5000)`: Connect to the hman using the given IP address and port.
- `disconnect()`: Disconnect from the hman.
- `set_mode(mode: str)`: Set the mode of the hman (available modes are: 'position', 'current', 'velocity', 'impedance').
- `set_cartesian_pos(posx: float, posy: float, posz: float)`: Set the cartesian position of the hman.
- `set_articular_pos(pos1: float, pos2: float, pos3: float)`: Set the articular position of the hman.
- `set_motors_current(cur1: float, cur2: float, cur3: float)`: Set the current of the hman's motors.
- `turn_off_current()`: Turn off the current of the hman's motors.
- `get_pos()`: Get the current position of the hman's motors.

## Contributions

Feel free to submit a pull request if you want to contribute to this project.

## License

This library is distributed under the MIT License. Please see the LICENSE file for more information.

## Support

If you have any questions or run into any problems, please open an issue in the GitHub repository.
7
## Disclaimer

Use this software at your own risk. The authors are not responsible for any damage that may be caused directly or indirectly through the use of this software.