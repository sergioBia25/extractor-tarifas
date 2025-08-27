# app.py
from  flask import Flask, render_template, request, send_file, url_for, jsonify
import os
import shutil
from src.tarifas_processor import TarifasElectricasProcessor
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from utils.csv_to_json_converter import CSVToJSONConverter

# Cargar variables de entorno
load_dotenv(os.path.join('private', '.env'))
API_KEY = os.getenv('ANTHROPIC_API_KEY')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

COMERCIALIZADORES = ["VATIA", "ENELX", "QI", "ENERTOTAL", "NEU", "ENERBIT"]

@app.route('/')
def index():
    return render_template('index.html', comercializadores=COMERCIALIZADORES)

@app.route('/procesar', methods=['POST'])
def procesar():
    archivo = request.files.get('archivo')
    comercializador = request.form.get('comercializador')

    if not archivo or archivo.filename == '':
        return 'No se seleccionó ningún archivo', 400
    if not comercializador:
        return 'No se seleccionó ningún comercializador', 400

    original_name = secure_filename(archivo.filename)
    original_path = os.path.join(app.config['UPLOAD_FOLDER'], original_name)
    archivo.save(original_path)

    try:
        processor = TarifasElectricasProcessor(api_key=API_KEY)
        # 1) Procesar CSV u otros formatos
        if original_name.lower().endswith('.csv'):
            csv_path = processor.procesar_csv(original_path, comercializador)
        else:
            csv_path, _ = processor.procesar_archivo(original_path, comercializador)

        # Validar salida CSV
        if not csv_path or not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
            return "El archivo CSV de salida no se generó correctamente", 500

        # 2) Convertir ese CSV procesado a JSON
        converter = CSVToJSONConverter()
        json_path = converter.convertir_csv_a_json(csv_path)
        if not json_path or not os.path.exists(json_path):
            return "Error al generar el archivo JSON", 500

        # 3) Mover ambos archivos a UPLOAD_FOLDER para que download_xxx los encuentre
        csv_name = secure_filename(os.path.basename(csv_path))
        target_csv = os.path.join(app.config['UPLOAD_FOLDER'], csv_name)
        if csv_path != target_csv:
            shutil.move(csv_path, target_csv)

        json_name = secure_filename(os.path.basename(json_path))
        target_json = os.path.join(app.config['UPLOAD_FOLDER'], json_name)
        if json_path != target_json:
            shutil.move(json_path, target_json)

        # 4) Devolver URLs en JSON
        return jsonify({
            'csv_url': url_for('download_csv', filename=csv_name),
            'json_url': url_for('download_json', filename=json_name)
        })

    except Exception as e:
        return f'Error al procesar el archivo: {str(e)}', 500

    finally:
        # Sólo eliminamos el archivo original subido
        if os.path.exists(original_path):
            os.remove(original_path)

@app.route('/download/csv/<filename>')
def download_csv(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(path):
        return 'Archivo no encontrado', 404
    return send_file(path, as_attachment=True, download_name=filename, mimetype='text/csv')

@app.route('/download/json/<filename>')
def download_json(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(path):
        return 'Archivo no encontrado', 404
    return send_file(path, as_attachment=True, download_name=filename, mimetype='application/json')

if __name__ == '__main__':
    app.run(debug=True)
