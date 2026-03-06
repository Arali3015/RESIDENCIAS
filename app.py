from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
import os  # Añade esta línea

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "Backend funcionando 🚀"


def get_db_connection():
    return mysql.connector.connect(
        host="crossover.proxy.rlwy.net",
        user="root",
        password="CVeroeIuMkDAETjhIDSHnkWoNejqmTwl",
        database="residencias",
        port=26100
    )


@app.route("/proyectos", methods=["GET"])
def obtener_proyectos():
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vista_proyectos")
        datos = cursor.fetchall()
        cursor.close()
        conexion.close()
        return jsonify(datos)
    except Exception as e:
        print("Error en /proyectos:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/registrar", methods=["POST"])
def registrar():
    try:
        datos = request.json
        print("Datos recibidos:", datos)

        conexion = get_db_connection()
        cursor = conexion.cursor()

        cursor.callproc("registrar_proyecto", [
            datos["nombre_alumno"],
            datos["apellido_alumno"],
            datos["matricula"],
            datos["nombre_ase_int"],
            datos["apellido_ase_int"],
            datos["nombre_ase_ext"],
            datos["apellido_ase_ext"],
            datos["nombre_empresa"],
            datos["nombre_periodo"],
            datos["fecha_inicio"],
            datos["fecha_fin"],
            datos["proyecto"]
        ])

        conexion.commit()
        cursor.close()
        conexion.close()

        return jsonify({"mensaje": "Proyecto registrado"})
    except Exception as e:
        print("Error en /registrar:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/eliminar/<int:id>", methods=["DELETE", "OPTIONS"])
def eliminar(id):
    # Manejar preflight CORS
    if request.method == "OPTIONS":
        response = jsonify({"mensaje": "OK"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        response.headers.add("Access-Control-Allow-Methods", "DELETE, OPTIONS")
        return response

    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()

        # Versión simple: solo eliminar el proyecto
        cursor.execute("DELETE FROM proyecto WHERE id_proyecto = %s", (id,))
        conexion.commit()

        filas_afectadas = cursor.rowcount
        cursor.close()
        conexion.close()

        response = jsonify({
            "mensaje": "Eliminado correctamente",
            "filas_afectadas": filas_afectadas
        })
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        print("Error en /eliminar:", str(e))
        response = jsonify({"error": str(e)}), 500
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

@app.route("/editar/<int:id>", methods=["PUT"])
def editar(id):
    try:
        data = request.json
        conexion = get_db_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE proyecto SET
                proyecto=%s,
                matricula=%s,
                nombre_alumno=%s,
                apellido_alumno=%s,
                nombre_ase_int=%s,
                apellido_ase_int=%s,
                nombre_ase_ext=%s,
                apellido_ase_ext=%s,
                nombre_empresa=%s,
                nombre_periodo=%s,
                fecha_inicio=%s,
                fecha_fin=%s
            WHERE id_proyecto=%s
        """, (
            data["proyecto"],
            data["matricula"],
            data["nombre_alumno"],
            data["apellido_alumno"],
            data["nombre_ase_int"],
            data["apellido_ase_int"],
            data["nombre_ase_ext"],
            data["apellido_ase_ext"],
            data["nombre_empresa"],
            data["nombre_periodo"],
            data["fecha_inicio"],
            data["fecha_fin"],
            id
        ))

        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({"mensaje": "Actualizado"})
    except Exception as e:
        print("Error en /editar:", str(e))
        return jsonify({"error": str(e)}), 500


# Endpoint de prueba para verificar la conexión
@app.route("/test", methods=["GET"])
def test():
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        # Probar conexión
        cursor.execute("SELECT 1")
        test_result = cursor.fetchone()

        # Ver si la vista existe
        cursor.execute("SHOW TABLES LIKE 'vista_proyectos'")
        vista_existe = cursor.fetchone()

        # Intentar obtener datos
        cursor.execute("SELECT * FROM proyecto LIMIT 5")
        datos_proyecto = cursor.fetchall()

        cursor.close()
        conexion.close()

        return jsonify({
            "conexion": "OK",
            "test_query": test_result,
            "vista_existe": vista_existe is not None,
            "datos_proyecto": datos_proyecto,
            "mensaje": "Backend funcionando correctamente"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "tipo_error": type(e).__name__
        }), 500


@app.route("/diagnostico", methods=["GET"])
def diagnostico():
    info = {
        "status": "OK",
        "endpoints_registrados": [],
        "variables_entorno": {
            "PORT": os.environ.get("PORT", "No definido")
        }
    }

    # Listar todas las rutas registradas
    for rule in app.url_map.iter_rules():
        info["endpoints_registrados"].append({
            "endpoint": rule.endpoint,
            "url": str(rule),
            "methods": list(rule.methods)
        })

    return jsonify(info)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)