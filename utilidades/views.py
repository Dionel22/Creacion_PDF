import io
import random
from django.http import FileResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

def generar_pdf_infinito(lista_numeros):
    buffer = io.BytesIO()
    # Márgenes pequeños para que entren bien las 20 filas
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                            rightMargin=5*mm, leftMargin=5*mm, 
                            topMargin=5*mm, bottomMargin=5*mm)
    elementos = []
    
    # Dividimos la lista total en grupos de 300 (uno por hoja)
    for i in range(0, len(lista_numeros), 300):
        bloque_300 = lista_numeros[i:i+300]
        
        # Organizamos ese bloque de 300 en filas de 15 columnas
        data = [bloque_300[j:j+15] for j in range(0, len(bloque_300), 15)]
        
        # Creamos la tabla (celdas rectangulares de 13mm de alto)
        tabla = Table(data, colWidths=13.3*mm, rowHeights=13*mm)
        tabla.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ]))
        
        elementos.append(tabla)
        
        # Si quedan más números, agregamos un salto de página
        if i + 300 < len(lista_numeros):
            elementos.append(PageBreak())
    
    doc.build(elementos)
    buffer.seek(0)
    return buffer

def vista_numeros(request):
    if 'lista_acumulada' not in request.session:
        request.session['lista_acumulada'] = []

    if request.method == "POST":
        if 'borrar_todo' in request.POST:
            request.session['lista_acumulada'] = []
            request.session.modified = True
            return redirect('numeros')

        if 'agregar' in request.POST:
            try:
                desde = int(request.POST.get('desde'))
                hasta = int(request.POST.get('hasta'))
                nuevos = list(range(desde, hasta + 1))
                lista_actual = request.session.get('lista_acumulada', [])
                
                # Evitar duplicados
                solo_nuevos = [n for n in nuevos if n not in lista_actual]
                lista_actual.extend(solo_nuevos)
                
                request.session['lista_acumulada'] = lista_actual
                request.session.modified = True
            except:
                messages.error(request, "Error al procesar los números.")

        if 'descargar' in request.POST:
            numeros_finales = list(request.session.get('lista_acumulada', []))
            # Solo ordenamos si el switch está marcado
            if request.POST.get('ordenar') == 'on':
                numeros_finales.sort()
            else:
                random.shuffle(numeros_finales)
            
            if numeros_finales:
                pdf = generar_pdf_infinito(numeros_finales)
                return FileResponse(pdf, as_attachment=True, filename='bingo_completo.pdf')

    numeros_vista = list(request.session.get('lista_acumulada', []))
    if request.POST.get('ordenar') == 'on':
        numeros_vista.sort()

    return render(request, 'utilidades/numeros.html', {
        'numeros': numeros_vista, # Mostramos todos en la web
        'total': len(numeros_vista)
    })