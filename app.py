
from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for
import json
import os
from datetime import datetime
import pdf_generator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Memoria temporal simple (en producción usaría DB o sesión)
current_entries = []

@app.route('/')
def index():
    return render_template('index.html', entries=current_entries, atas=get_atas())

@app.route('/delete/<int:entry_id>')
def delete_entry(entry_id):
    if 0 <= entry_id < len(current_entries):
        current_entries.pop(entry_id)
    return redirect(url_for('index'))

@app.route('/edit/<int:entry_id>')
def edit_entry_page(entry_id):
    if 0 <= entry_id < len(current_entries):
        entry_to_edit = current_entries[entry_id]
        return render_template('index.html', entries=current_entries, atas=get_atas(), edit_entry=entry_to_edit, edit_id=entry_id)
    return redirect(url_for('index'))

@app.route('/update/<int:entry_id>', methods=['POST'])
def update_entry(entry_id):
    if 0 <= entry_id < len(current_entries):
        data = request.form
        entry = {
            "ata": data.get('ata'),
            "descripcion": data.get('descripcion'),
            "modelo": data.get('modelo'),
            "matricula": data.get('matricula'),
            "fecha": data.get('fecha')
        }
        # Asegurar EC-
        if not entry['matricula'].upper().startswith('EC'):
            entry['matricula'] = 'EC-' + entry['matricula']
        if entry['matricula'].upper().startswith('EC-EC-'):
            entry['matricula'] = entry['matricula'][3:]
            
        current_entries[entry_id] = entry
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add_entry():
    data = request.form
    entry = {
        "ata": data.get('ata'),
        "descripcion": data.get('descripcion'),
        "modelo": data.get('modelo'),
        "matricula": data.get('matricula'),
        "fecha": data.get('fecha')
    }
    # Asegurar EC-
    if not entry['matricula'].upper().startswith('EC'):
        entry['matricula'] = 'EC-' + entry['matricula']
    if entry['matricula'].upper().startswith('EC-EC-'):
         entry['matricula'] = entry['matricula'][3:]

    current_entries.append(entry)
    return redirect(url_for('index'))

@app.route('/upload_json', methods=['POST'])
def upload_json():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        try:
            entries = json.load(file)
            if isinstance(entries, list):
                global current_entries
                current_entries = entries # Reemplazar o añadir? Reemplazamos para cargar estado.
                # Opcional: Validar estructura
        except Exception as e:
            print(f"Error cargando JSON: {e}")
    
    return redirect(url_for('index'))

@app.route('/download_json')
def download_json():
    return jsonify(current_entries)

@app.route('/generate_pdf')
def generate_pdf():
    global current_entries
    if not current_entries:
        return "No hay datos para generar PDF", 400
    
    output_path = os.path.join("static", "Registro_Experiencia_WEB.pdf")
    
    # Usar la lógica existente que ya calibramos
    success = pdf_generator.generate_final_pdf(current_entries, output_path=output_path)
    
    if success:
        return send_file(output_path, as_attachment=True)
    else:
        return "Error generando PDF", 500

@app.route('/clear')
def clear():
    global current_entries
    current_entries = []
    return redirect(url_for('index'))

def get_atas():
    return [
            "05 - TIME LIMITS/MAINTENANCE CHECKS",
            "06 - DIMENSIONS AND AREAS",
            "07 - LIFTING AND SHORING",
            "08 - LEVELING AND WEIGHING",
            "09 - TOWING AND TAXIING",
            "10 - PARKING, MOORING, STORAGE AND RETURN TO SERVICE",
            "11 - PLACARDS AND MARKINGS",
            "12 - SERVICING",
            "18 - VIBRATION AND NOISE ANALYSIS (HELICOPTER ONLY)",
            "20 - STANDARD PRACTICES – AIRFRAME",
            "21 - AIR CONDITIONING",
            "22 - AUTO FLIGHT",
            "23 - COMMUNICATIONS",
            "24 - ELECTRICAL POWER",
            "25 - EQUIPMENT/FURNISHINGS",
            "26 - FIRE PROTECTION",
            "27 - FLIGHT CONTROLS",
            "28 - FUEL",
            "29 - HYDRAULIC POWER",
            "30 - ICE AND RAIN PROTECTION",
            "31 - INDICATING/RECORDING SYSTEMS",
            "32 - LANDING GEAR",
            "33 - LIGHTS",
            "34 - NAVIGATION",
            "35 - OXYGEN",
            "36 - PNEUMATIC",
            "37 - VACUUM",
            "38 - WATER/WASTE",
            "39 - ELECTRICAL - ELECTRONIC PANELS AND MULTIPURPOSE COMPONENTS",
            "41 - WATER BALLAST",
            "42 - INTEGRATED MODULAR AVIONICS",
            "44 - CABIN SYSTEMS",
            "45 - DIAGNOSTIC AND MAINTENANCE SYSTEM",
            "46 - INFORMATION SYSTEMS",
            "47 - NITROGEN GENERATION SYSTEM",
            "48 - IN FLIGHT FUEL DISPENSING",
            "49 - AIRBORNE AUXILIARY POWER",
            "50 - CARGO AND ACCESSORY COMPARTMENTS",
            "51 - STANDARD PRACTICES AND STRUCTURES - GENERAL",
            "52 - DOORS",
            "53 - FUSELAGE",
            "54 - NACELLES/PYLONS",
            "55 - STABILIZERS",
            "56 - WINDOWS",
            "57 - WINGS",
            "60 - STANDARD PRACTICES - PROPELLER/ROTOR",
            "61 - PROPELLERS",
            "62 - MAIN ROTOR(S)",
            "63 - MAIN ROTOR DRIVE(S)",
            "64 - TAIL ROTOR",
            "65 - TAIL ROTOR DRIVE",
            "66 - ROTOR BLADE AND TAIL PYLON FOLDING",
            "67 - ROTORS FLIGHT CONTROL",
            "70 - STANDARD PRACTICES - ENGINE",
            "71 - POWER PLANT",
            "72 - ENGINE",
            "73 - ENGINE - FUEL AND CONTROL",
            "74 - IGNITION",
            "75 - BLEED AIR",
            "76 - ENGINE CONTROLS",
            "77 - ENGINE INDICATING",
            "78 - EXHAUST",
            "79 - OIL",
            "80 - STARTING",
            "81 - TURBINES (RECIPROCATING ENGINES)",
            "82 - WATER INJECTION",
            "83 - ACCESSORY GEAR BOXES",
            "84 - PROPULSION AUGMENTATION",
            "91 - CHARTS"
    ]

if __name__ == '__main__':
    app.run(debug=True, port=5000)
