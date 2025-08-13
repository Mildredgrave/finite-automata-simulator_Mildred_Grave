from flask import json

class Archive:
    def __init__(self, archive):
        self.__archive = archive
        self.__cleanarchive = self.change()  # Llama al método

    def initializer(self):
        return self.__cleanarchive

    def change(self):
        if self.__archive:
            try:
                content_bytes = self.__archive.read()
                content_string = content_bytes.decode('utf-8')
                json_content = json.loads(content_string)
                return json_content, 200
            except json.JSONDecodeError:
                return "Error: el archivo no es JSON válido", 400
        else:
            return "No se recibió ningún archivo", 400
