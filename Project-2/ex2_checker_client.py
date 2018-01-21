from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client
import socket
from multiprocessing import Process
import ex2
import traceback
import sys


def convert_dictionary_to_string_keys(d):
    newd = {}
    for k in d:
        newd[repr(k)] = d[k]
    return newd


def get_num_of_transmitters(Lazer_transm_tuple):
    [x_y_trans, x_z_tran, y_z_tran] = Lazer_transm_tuple
    num_of_transmitters = len(x_y_trans) + len(x_z_tran) + len(y_z_tran)
    return num_of_transmitters


def check_solution(problem, lazer_locations):
    controller = ex2.SpaceshipController(problem, get_num_of_transmitters(lazer_locations))


    hostname = socket.gethostname()
    # print("hostname", hostname)
    ipaddress = socket.gethostbyname(socket.gethostname())

    # print("IP address", ipaddress)

    # Restrict to a particular path.
    class RequestHandler(SimpleXMLRPCRequestHandler):
        rpc_paths = ('/RPC2',)

    server = SimpleXMLRPCServer(("0.0.0.0", 40021),
                                requestHandler=RequestHandler, allow_none=True)

    done = False

    def ex2_get_next_action(observation):
        print("Received Observation: ", observation)
        try:
            action = controller.get_next_action(observation)
            print("Returned Action: ", action)
            return action
        except:
            traceback.print_exc()
            return ""

    def report(message):
        print("from server: ", message)

    def finished():
        # print("finished")
        server.server_close()
        done = True

    # Create server
    def serve_policy():
        # print("creating query policy server")
        server.register_function(ex2_get_next_action, 'ex2_get_next_action')
        server.register_function(report, 'report')
        server.register_function(finished, 'finished')
        # print("starting query policy server")
        try:
            while not done:
                server.handle_request()
        except Exception as e:
            pass
            # print(e)
        # print("stopping query policy server")

    p = Process(target=serve_policy)
    p.start()

    s = xmlrpc.client.ServerProxy('http://172.17.0.1:40002', allow_none=True)
    # s = SimpleXMLRPCServer(("127.0.0.1",40002), allow_none=True)
    # s = xmlrpc.client.ServerProxy('http://127.0.0.1:40002', allow_none=True)

    print(s.handle_ex2(ipaddress, problem[0:5] + (convert_dictionary_to_string_keys(problem[5]),) + problem[6:],
                       lazer_locations))
    p.join()
