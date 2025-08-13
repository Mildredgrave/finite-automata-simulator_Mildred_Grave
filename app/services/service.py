import os
import time
from flask import json
import graphviz

class Archive:
    def __init__(self, file):
        self.__file = file
        self.__clean_file = self.load()

    def initializer(self):
        return self.__clean_file

    def load(self):
        if self.__file:
            try:
                content_bytes = self.__file.read()
                content_string = content_bytes.decode('utf-8')
                json_content = json.loads(content_string)
                return json_content, 200
            except json.JSONDecodeError:
                return "Error: The file is not valid JSON", 400
        else:
            return "No file received", 400


def format_transitions(transitions_list):
    """
    Convert JSON transitions list to a dictionary {from_state: {symbol: to_state}}
    """
    trans_dict = {}
    for t in transitions_list:
        origin = t["from_state"]
        symbol = t["symbol"]
        destination = t["to_state"]
        if origin not in trans_dict:
            trans_dict[origin] = {}
        trans_dict[origin][symbol] = destination
    return trans_dict


class AutomatonProcessor:
    def __init__(self, automaton):
        self.automaton = automaton
        self.errors = []

    def validate(self):
        states = self.automaton.get("states")
        alphabet = self.automaton.get("alphabet")
        transitions = self.automaton.get("transitions")
        initial = self.automaton.get("initial_state")
        acceptance = self.automaton.get("acceptance_states")

        if not states or not isinstance(states, list):
            self.errors.append("States are not defined or type is incorrect.")
        if not alphabet or not isinstance(alphabet, list):
            self.errors.append("Alphabet is not defined or type is incorrect.")
        if initial not in states:
            self.errors.append(f"Initial state '{initial}' does not exist.")
        if not acceptance:
            self.errors.append("No acceptance states defined in the automaton.")
        elif not set(acceptance).issubset(states):
            self.errors.append("Some acceptance states do not exist in the list of states.")

        for origin, trans in transitions.items():
            for symbol in trans.keys():
                if symbol not in alphabet:
                    self.errors.append(f"Symbol '{symbol}' is not in the alphabet.")

        for origin, trans in transitions.items():
            if origin not in states:
                self.errors.append(f"Origin state '{origin}' in transitions is not defined.")
            for destination in trans.values():
                if destination not in states:
                    self.errors.append(f"Destination '{destination}' does not exist.")

        for state in states:
            if state not in transitions:
                self.errors.append(f"State '{state}' does not have defined transitions.")

        return not self.errors

    def process(self, automaton_id):
        if not self.validate():
            return {"id": automaton_id, "status": "error", "errors": self.errors}

        import os, time, graphviz

        os.makedirs("generated_diagrams", exist_ok=True)
        filename = f"{automaton_id}_{int(time.time())}.png"
        filepath = os.path.join("generated_diagrams", filename)

        dot = graphviz.Digraph(format="png")
        dot.attr('node', shape='point')
        dot.node('start')
        dot.edge('start', self.automaton["initial_state"])

        for state in self.automaton["states"]:
            if state in self.automaton["acceptance_states"]:
                # Estado de aceptación: doble círculo + color amarillo
                dot.node(state, shape='doublecircle', style='filled', fillcolor='yellow')
            else:
                dot.node(state, shape='circle')

        for origin, trans in self.automaton["transitions"].items():
            for symbol, destination in trans.items():
                dot.edge(origin, destination, label=symbol)

        dot.render(filepath, cleanup=True)

        return {
            "id": automaton_id,
            "status": "success",
            "message": "Automaton processed successfully.",
            "diagram_path": filepath
        }

