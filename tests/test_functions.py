from pyhman import hman, hmanserver

def test_communication():
    #create a hmanserver to simulate the hman
    server = hmanserver.HmanServer(3, True)
    server.set_positions([1, 2, 3])
    #start the server
    server.start()
    #create a hman object
    hman = hman.Hman()
    hman = hman.Hman(3, True)
    #connect to the hman
    hman.connect('localhost')
    #set articular position
    pos = hman.set_articular_pos(2, 3, 4)
    assert pos == [1, 2, 3]