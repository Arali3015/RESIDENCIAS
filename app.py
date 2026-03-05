from idlelib.pyshell import PORT

from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

conexion = mysql.connector.connect(
    host="crossover.proxy.rlwy.net",
    user="root",
    password="CVeroeIuMkDAETjhIDSHnkWoNejqmTwl",
    database="residencias",
    port=26100
)

@app.route("/proyectos", methods=["GET"])
def obtener_proyectos():
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM vista_proyectos")
    datos = cursor.fetchall()
    return jsonify(datos)

@app.route("/registrar", methods=["POST"])
def registrar():
    datos = request.json
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
    return {"mensaje": "Proyecto registrado"}

@app.route("/eliminar/<int:id>", methods=["DELETE"])
def eliminar(id):
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM proyecto WHERE id_proyecto = %s", (id,))
    conexion.commit()
    return jsonify({"mensaje": "Eliminado"})

@app.route("/editar/<int:id>", methods=["PUT"])
def editar(id):
    data = request.json
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
    return jsonify({"mensaje": "Actualizado"})

if __name__ == "__main__":
    app.run()