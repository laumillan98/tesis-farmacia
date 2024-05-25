from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from datetime import datetime

def header_footer(canvas, doc, user, entity):
    canvas.saveState()
    width, height = landscape(A4)
    image = 'C:/Users/laumi/Downloads/example/FirstApp/static/dist/img/InfomedLogo.png'
    
    # Header
    image_width = 50
    image_height = 50
    image_x = 50
    image_y = height - image_height - 30  # Ajustar la posición vertical de la imagen

    canvas.drawImage(image, image_x, image_y, width=image_width, height=image_height, mask='auto')

    text_x = image_x + image_width + 10
    text_y = image_y + 25  # Centrar verticalmente con la imagen
    canvas.setFont('Helvetica', 10)
    canvas.drawString(text_x, text_y + 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d')}")
    canvas.drawString(text_x, text_y - 5, f"Usuario: {user}")
    canvas.drawString(text_x, text_y - 20, f"Entidad Exportada: {entity}")

    canvas.line(50, image_y - 15, width - 50, image_y - 10)
    
    canvas.restoreState()