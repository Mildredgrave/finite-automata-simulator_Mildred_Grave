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
                return "Error: el archivo no es JSON válido", 400
        else:
            return "No se recibió ningún archivo", 400

def format_transitions(transitions_list):
    """
    Convierte la lista de transiciones del JSON en un diccionario
    {origen: {simbolo: destino}}
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
            self.errors.append("Estados no definidos o tipo incorrecto.")
        if not alphabet or not isinstance(alphabet, list):
            self.errors.append("Alfabeto no definido o tipo incorrecto.")
        if not initial:
            self.errors.append("No hay estado inicial definido para el autómata")
        elif initial not in states:
            self.errors.append(f"Estado Inicial '{initial}' no existe.")
        if not acceptance:
            self.errors.append("No hay estados de aceptación en el autómata.")
        elif not set(acceptance).issubset(states):
            self.errors.append("Algún estado de aceptación no existe en la lista de estados.")

        if transitions:
            for origin, trans in transitions.items():
                for symbol in trans.keys():
                    if symbol not in alphabet:
                        self.errors.append(f"Simbolo '{symbol}' no está en el alfabeto.")

            for origin, trans in transitions.items():
                if origin not in states:
                    self.errors.append(f"Estado '{origin}' en transiciones no está definido.")
                for destination in trans.values():
                    if destination not in states:
                        self.errors.append(f"Destino '{destination}' no existe.")

            for state in states:
                if state not in transitions:
                    self.errors.append(f"Estado '{state}' no tiene transiciones definidas.")
        else:
            self.errors.append("No hay transiciones definidas.")

        return not self.errors

    def validate_input(self, input_str):
        """
        Valida una cadena de entrada en el autómata.
        Retorna True si es aceptada, False si no.
        """
        current_state = self.automaton.get("initial_state")
        transitions = self.automaton.get("transitions")
        acceptance = self.automaton.get("acceptance_states")
        for symbol in input_str:
            if symbol not in self.automaton.get("alphabet", []):
                return False
            current_state = transitions.get(current_state, {}).get(symbol)
            if current_state is None:
                return False
        return current_state in acceptance

    def process(self, automaton_id, inputs=None):
        if not self.validate():
            return {
                "id": automaton_id,
                "success": False,
                "error_description": self.errors[0] if self.errors else "Error desconocido"
            }

        # Genera el diagrama 
        os.makedirs("generated_diagrams", exist_ok=True)
        filename = f"{automaton_id}_{int(time.time())}.png"
        filepath = os.path.join("generated_diagrams", filename)

        dot = graphviz.Digraph(format="png")
        dot.attr('node', shape='point')
        dot.node('start')
        dot.edge('start', self.automaton["initial_state"])

        for state in self.automaton["states"]:
            if state in self.automaton["acceptance_states"]:
                dot.node(state, shape='doublecircle', style='filled', fillcolor='yellow')
            else:
                dot.node(state, shape='circle')

        for origin, trans in self.automaton["transitions"].items():
            for symbol, destination in trans.items():
                dot.edge(origin, destination, label=symbol)

        dot.render(filepath, cleanup=True)

        inputs_validation = []
        if inputs is not None:
            for input_str in inputs:
                result = self.validate_input(input_str)
                inputs_validation.append({
                    "input": input_str,
                    "result": result
                })

        return {
            "id": automaton_id,
            "success": True,
            "inputs_validation": inputs_validation
        }

def process_automata_list(automata_list):
    """
    Procesa una lista de autómatas y devuelve la respuesta en el formato requerido.
    """
    respuesta = []
    for automaton_data in automata_list:
        automaton = automaton_data.copy()
        # Convertir transiciones a diccionario
        automaton["transitions"] = format_transitions(automaton_data["transitions"])
        processor = AutomatonProcessor(automaton)
        result = processor.process(
            automaton_id=automaton_data["id"],
            inputs=automaton_data.get("test_strings", [])
        )
        if not result["success"]:
            result.pop("inputs_validation", None)
        respuesta.append(result)
    return respuesta