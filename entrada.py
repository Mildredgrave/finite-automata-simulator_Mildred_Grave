from app.run import app
from waitress import serve

#if __name__ == '__main__':
#    print("Iniciando el servidor de desarrollo de Flask con modo debug activado...")
#    app.run(debug=True, port=5001)

if __name__ == '__main__':
    try:
        serve(app, port=3001
    )
    except Exception as e:
        print(f"Ocurrió un error: {e}")
