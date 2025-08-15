import io
import unittest
from unittest.mock import patch
from services.service import Archive, AutomatonProcessor, process_automata_list, format_transitions


class TestArchive(unittest.TestCase):

    def test_load_valid_json(self):
        file = io.BytesIO(b'{"key": "value"}')
        archive = Archive(file)
        data, status = archive.load()
        self.assertEqual(status, 200)
        self.assertEqual(data, {"key": "value"})

    def test_load_invalid_json(self):
        file = io.BytesIO(b'invalid json')
        archive = Archive(file)
        data, status = archive.load()
        self.assertEqual(status, 400)
        self.assertIn("Error", data)

    def test_load_no_file(self):
        archive = Archive(None)
        data, status = archive.load()
        self.assertEqual(status, 400)
        self.assertIn("No se recibió", data)

class TestAutomatonProcessor(unittest.TestCase):

    def setUp(self):
        self.automaton_valid = {
            "states": ["q0", "q1"],
            "alphabet": ["0", "1"],
            "transitions": {"q0": {"0": "q0", "1": "q1"}, "q1": {"0": "q1", "1": "q0"}},
            "initial_state": "q0",
            "acceptance_states": ["q1"]
        }
        self.automaton_invalid = {
            "states": ["q0"],
            "alphabet": ["0", "1"],
            "transitions": {},
            "initial_state": "q2",
            "acceptance_states": ["q3"]
        }

    def test_validate_valid_automaton(self):
        processor = AutomatonProcessor(self.automaton_valid)
        self.assertTrue(processor.validate())
        self.assertEqual(processor.errors, [])

    def test_validate_invalid_automaton(self):
        processor = AutomatonProcessor(self.automaton_invalid)
        self.assertFalse(processor.validate())
        self.assertTrue(len(processor.errors) > 0)

    def test_validate_input_accepted(self):
        processor = AutomatonProcessor(self.automaton_valid)
        processor.validate()
        self.assertTrue(processor.validate_input("1"))
        self.assertFalse(processor.validate_input("11"))

    @patch("graphviz.Digraph.render")  # Evita crear archivos durante la prueba
    def test_process(self, mock_render):
        processor = AutomatonProcessor(self.automaton_valid)
        result = processor.process("automaton1", inputs=["0", "1"])
        self.assertTrue(result["success"])
        self.assertEqual(len(result["inputs_validation"]), 2)

class TestProcessAutomataList(unittest.TestCase):

    @patch("graphviz.Digraph.render")  # Evita crear archivos
    def test_process_automata_list(self, mock_render):
        automata_list = [
            {
                "id": "autom1",
                "states": ["q0", "q1"],
                "alphabet": ["a", "b"],
                "transitions": [{"from_state": "q0", "symbol": "a", "to_state": "q1"}],
                "initial_state": "q0",
                "acceptance_states": ["q1"],
                "test_strings": ["a", "b"]
            }
        ]
        result = process_automata_list(automata_list)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0]["success"])
        self.assertEqual(result[0]["inputs_validation"][0]["result"], True)
        self.assertEqual(result[0]["inputs_validation"][1]["result"], False)

if __name__ == "__main__":
    unittest.main()
