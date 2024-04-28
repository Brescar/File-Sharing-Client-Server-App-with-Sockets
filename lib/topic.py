import threading
from .serialize import Response
from .serialize import Request

class StateMachine:
    def __init__(self, client, global_state):
        self.transitions = {}
        self.start_state = None
        self.end_states = []
        self.current_state = None
        self.global_state = global_state
        self.client = client

    def add_transition(self, state_name, command, transition, end_state=0):
        self.transitions.setdefault(state_name, {})
        self.transitions[state_name][command] = transition
        if end_state:
            self.end_states.append(state_name)

    def set_start(self, name):
        self.start_state = name
        self.current_state = name

    def process_command(self, unpacked_request):
        print('state before %s' % self.current_state)
        if unpacked_request.type not in self.transitions[self.current_state]:
            valid_commands = ', '.join(self.transitions[self.current_state].keys())
            return Response(-4, f'Invalid command. Valid commands are: {valid_commands}')
        handler = self.transitions[self.current_state][unpacked_request.type]
        (new_state, response) = handler(unpacked_request, self.global_state, self.client)
        self.current_state = new_state
        print('state after %s' % self.current_state)
        return response

class TopicProtocol(StateMachine):
    def __init__(self, client, global_state, transitions_list):
        super().__init__(client, global_state)
        self.set_start('start')
        for transition in transitions_list:
            self.add_transition(transition[0], transition[1], transition[2])

class TopicList:
    def __init__(self):
        self.clients = []
        self.logged_in_users = []
        self.client_user_map = {}
        self.lock = threading.Lock()

    def add_client(self, client):
        with self.lock:
            self.clients.append(client)

    def remove_client(self, client):
        with self.lock:
            self.clients.remove(client)