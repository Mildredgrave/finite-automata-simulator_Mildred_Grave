from flask import Blueprint, request, jsonify
from app.services.service import Archive, AutomatonProcessor, format_transitions

load_archive = Blueprint('load_archive', __name__)

@load_archive.route("/process-automaton", methods=["POST"])
def process_automaton():
    if 'file' not in request.files:
        return jsonify({"error": "No se envio archivo JSON"}), 400

    file = request.files['file']

    archive = Archive(file)
    json_content, status = archive.initializer()
    if status != 200:
        return jsonify({"error": json_content}), status

    results = []
    for automaton in json_content:
        automaton["transitions"] = format_transitions(automaton["transitions"])
        processor = AutomatonProcessor(automaton)
        result = processor.process(automaton["id"])
        results.append(result)

    return jsonify(results), 200
