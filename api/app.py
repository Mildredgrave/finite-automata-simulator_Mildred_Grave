import os
import time
import json
from flask import Flask, request, jsonify, current_app
from simulator.validator import validate_automaton_schema, ValidationError
from simulator.automaton import Automaton
from simulator.diagram_generator import DiagramGenerator

app = Flask(__name__)
app.config['GENERATE_DIR'] = 'generated_diagram'  # carpeta para guardar los diagramas generados

@app.route('/process_automata', methods=['POST'])
def process_automata():
    try:
        # Lee lista de autómatas del archivo o JSON enviado
        if 'file' in request.files:
            file = request.files['file']
            content = file.read()
            automata_list = json.loads(content)
        else:
            automata_list = request.get_json()
            if automata_list is None:
                return jsonify({"error": "Invalid JSON in request body"}), 400
        
        if not isinstance(automata_list, list):
            return jsonify({"error": "Input should be a list of automata"}), 400
        
        results = []
        output_dir = current_app.config.get('GENERATE_DIR', 'generated_diagram')
        os.makedirs(output_dir, exist_ok=True)
        diagram_generator = DiagramGenerator(output_dir)

        for automaton_json in automata_list:
            automaton_id = automaton_json.get('id', '<unknown>')
            try:
                validate_automaton_schema(automaton_json)
                automaton = Automaton.from_dict(automaton_json)
                
                timestamp = int(time.time())
                diagram_filename = f"automaton_{automaton_id}_{timestamp}"
                diagram_path = diagram_generator.generate(automaton, diagram_filename)
                
                test_strings = automaton_json.get('test_string', [])
                inputs_validation = []
                for s in test_strings:
                    result = automaton.process_string(s)
                    inputs_validation.append({
                        "input": s,
                        "result": result
                    })
                
                results.append({
                    "id": automaton_id,
                    "success": True,
                    "diagram": diagram_path,
                    "inputs_validation": inputs_validation
                })

            except ValidationError as ve:
                results.append({
                    "id": automaton_id,
                    "success": False,
                    "error": str(ve)
                })
            except Exception as e:
                results.append({
                    "id": automaton_id,
                    "success": False,
                    "error": f"Processing error: {str(e)}"
                })

        return jsonify(results), 200

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON file or body"}), 400
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
