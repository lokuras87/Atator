
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from pypdf import PdfReader, PdfWriter

TEMPLATE_PATH = "template.pdf"
OUTPUT_FILENAME = "Registro_Experiencia.pdf"

# Coordenadas ajustadas basadas en análisis del PDF (Landscape)
# Página A4 Landscape: 842 x 595 puntos

# Coordenadas X de las columnas (Ajustadas a los encabezados detectados)
X_ATA = 66       # Ajuste: Un poco a la izquierda para 2 cifras (era 72)
X_DESCRIPCION = 105 # (Sin cambios)
X_MODELO = 535   # Ajuste: Más a la derecha para centrar (era 515)
X_MATRICULA = 637 # Header "Matricula" at 637
X_FECHA = 720    # Header "Fecha" at 721

# Coordenada Y de la primera fila
# Ajuste V4: El usuario pide probar con 26.0
Y_START = 425 
ROW_HEIGHT = 26.0
MAX_ROWS_PER_PAGE = 12

def create_overlay_pdf(entries):
    """
    Crea un PDF en memoria con solo el texto de las entradas.
    Maneja múltiples páginas si hay muchas entradas.
    Retorna una lista de objetos BytesIO (uno por página de datos).
    """
    pages_overlays = []
    
    current_buffer = io.BytesIO()
    # USAR LANDSCAPE A4
    c = canvas.Canvas(current_buffer, pagesize=landscape(A4))
    c.setFont("Helvetica", 10)
    
    y = Y_START
    row_count = 0
    
    for entry in entries:
        ata = entry.get("ata", "")
        desc = entry.get("descripcion", "")
        model = entry.get("modelo", "")
        reg = entry.get("matricula", "")
        date = entry.get("fecha", "")

        # Dibujar campos
        c.drawString(X_ATA, y, str(ata).split(" - ")[0]) # Solo número ATA
        
        # Manejo básico de texto largo en descripción
        if len(desc) > 60: # Más ancho disponible en landscape
             desc = desc[:57] + "..."
        c.drawString(X_DESCRIPCION, y, desc)
        
        c.drawString(X_MODELO, y, model)
        c.drawString(X_MATRICULA, y, reg)
        c.drawString(X_FECHA, y, date)
        
        y -= ROW_HEIGHT
        row_count += 1
        
        # Si llenamos la página, terminamos este canvas y empezamos otro
        if row_count >= MAX_ROWS_PER_PAGE:
            c.showPage() # Finaliza la página actual
            c.save()
            current_buffer.seek(0)
            pages_overlays.append(current_buffer)
            
            # Reiniciar para la siguiente página
            current_buffer = io.BytesIO()
            c = canvas.Canvas(current_buffer, pagesize=landscape(A4))
            c.setFont("Helvetica", 10)
            y = Y_START
            row_count = 0

    c.save()
    current_buffer.seek(0)
    pages_overlays.append(current_buffer)
    
    return pages_overlays

def generate_final_pdf(entries, output_path=OUTPUT_FILENAME):
    if not os.path.exists(TEMPLATE_PATH):
        print(f"Error: No se encuentra la plantilla {TEMPLATE_PATH}")
        return False

    overlays = create_overlay_pdf(entries)
    
    template_reader = PdfReader(TEMPLATE_PATH)
    template_page = template_reader.pages[0] # Asumimos que la plantilla es de 1 página
    
    writer = PdfWriter()

    for overlay_data in overlays:
        # Crear lector para la capa de texto
        overlay_reader = PdfReader(overlay_data)
        if len(overlay_reader.pages) > 0:
            overlay_page = overlay_reader.pages[0]
            
            # Clonar la página de plantilla para no modificar la original en memoria repetidamente
            # Nota: pypdf maneja referencias, así que mejor fusionar sobre una copia "limpia" 
            # o simplemente fusionar la plantilla SOBRE el contenido (o al revés).
            
            # Estrategia: Crear una página en blanco, fusionar plantilla, luego fusionar texto.
            # O más simple: Cargar plantilla, fusionar texto.
            
            # Para pypdf moderno:
            # 1. Copiar la página de la plantilla
            # 2. Fusionar el overlay (texto) encima
            
            writer.add_page(template_page)
            # La página recién añadida es la última
            current_page = writer.pages[-1]
            current_page.merge_page(overlay_page)
    
    try:
        with open(output_path, "wb") as f:
            writer.write(f)
        print(f"PDF generado correctamente en: {output_path}")
        return True
    except Exception as e:
        print(f"Error generando PDF final: {e}")
        return False
