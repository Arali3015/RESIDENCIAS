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


@app.route("/eliminar/<int:id>", methods=["DELETE"])
def eliminar(id):
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)

        # Primero obtenemos los IDs relacionados
        cursor.execute("""
            SELECT id_alumno, id_asesor_interno, id_asesor_externo, id_empresa, id_periodo 
            FROM proyecto WHERE id_proyecto = %s
        """, (id,))

        resultado = cursor.fetchone()
        print(f"Resultado de búsqueda para ID {id}:", resultado)  # Debug

        if resultado:
            id_alumno = resultado['id_alumno']
            id_asi_int = resultado['id_asesor_interno']
            id_asi_ext = resultado['id_asesor_externo']
            id_empresa = resultado['id_empresa']
            id_periodo = resultado['id_periodo']

            # Eliminar el proyecto
            cursor.execute("DELETE FROM proyecto WHERE id_proyecto = %s", (id,))
            print(f"Proyecto {id} eliminado")  # Debug

            # Verificar y eliminar registros huérfanos
            cursor.execute("SELECT COUNT(*) as count FROM proyecto WHERE id_alumno = %s", (id_alumno,))
            if cursor.fetchone()['count'] == 0:
                cursor.execute("DELETE FROM alumnos WHERE id_alumno = %s", (id_alumno,))
                print(f"Alumno {id_alumno} eliminado")  # Debug

            cursor.execute("SELECT COUNT(*) as count FROM proyecto WHERE id_asesor_interno = %s", (id_asi_int,))
            if cursor.fetchone()['count'] == 0:
                cursor.execute("DELETE FROM asesores WHERE id_asesor = %s", (id_asi_int,))
                print(f"Asesor interno {id_asi_int} eliminado")  # Debug

            cursor.execute("SELECT COUNT(*) as count FROM proyecto WHERE id_asesor_externo = %s", (id_asi_ext,))
            if cursor.fetchone()['count'] == 0:
                cursor.execute("DELETE FROM asesores WHERE id_asesor = %s", (id_asi_ext,))
                print(f"Asesor externo {id_asi_ext} eliminado")  # Debug

            cursor.execute("SELECT COUNT(*) as count FROM proyecto WHERE id_empresa = %s", (id_empresa,))
            if cursor.fetchone()['count'] == 0:
                cursor.execute("DELETE FROM empresa WHERE id_empresa = %s", (id_empresa,))
                print(f"Empresa {id_empresa} eliminada")  # Debug

            cursor.execute("SELECT COUNT(*) as count FROM proyecto WHERE id_periodo = %s", (id_periodo,))
            if cursor.fetchone()['count'] == 0:
                cursor.execute("DELETE FROM periodo WHERE id_periodo = %s", (id_periodo,))
                print(f"Periodo {id_periodo} eliminado")  # Debug

            conexion.commit()
            print("Transacción completada exitosamente")  # Debug
        else:
            print(f"No se encontró proyecto con ID {id}")  # Debug
            return jsonify({"error": "Proyecto no encontrado"}), 404

        cursor.close()
        conexion.close()

        return jsonify({"mensaje": "Eliminado correctamente"})

    except Exception as e:
        print("Error en /eliminar:", str(e))
        import traceback
        traceback.print_exc()  # Esto imprimirá el error completo
        return jsonify({"error": str(e)}), 500

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