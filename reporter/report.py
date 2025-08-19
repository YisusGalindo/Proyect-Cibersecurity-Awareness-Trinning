import os, requests, io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
import matplotlib.pyplot as plt
import matplotlib.patches as patches

API = os.getenv('GOPHISH_URL','http://localhost:3333')
KEY = os.getenv('GOPHISH_API_KEY','').strip()
CID = os.getenv('CAMPAIGN_ID','').strip()
OUT = '/out'

headers = {'Authorization': f'Bearer {KEY}'}

print(f"Generando reporte para campaña {CID}...")

try:
    r = requests.get(f"{API}/api/campaigns/{CID}", headers=headers)
    r.raise_for_status()
    data = r.json()
    results = data.get('results', [])
    campaign_name = data.get('name', f'Campaña {CID}')
    
    print(f"Campaña encontrada: {campaign_name}")
    print(f"Total de objetivos: {len(results)}")

    # Análisis detallado de resultados
    counts = {
        'Enviado': 0,
        'Entregado/Abierto': 0,
        'Clic': 0,
        'Credenciales': 0,
        'Reportado': 0
    }
    
    details_by_dept = {
        'TI': {'total': 0, 'clicked': 0, 'submitted': 0, 'users': []},
        'Finanzas': {'total': 0, 'clicked': 0, 'submitted': 0, 'users': []},
        'HR': {'total': 0, 'clicked': 0, 'submitted': 0, 'users': []},
        'Operaciones': {'total': 0, 'clicked': 0, 'submitted': 0, 'users': []}
    }
    
    vulnerable_users = []
    
    for e in results:
        status = e.get('status','')
        email = e.get('email', '')
        
        # Determinar departamento
        dept = 'TI'
        if 'ana.perez' in email:
            dept = 'Finanzas'
        elif 'john.smith' in email:
            dept = 'HR'
        elif 'mary.johnson' in email:
            dept = 'Operaciones'
        
        details_by_dept[dept]['total'] += 1
        details_by_dept[dept]['users'].append({
            'email': email,
            'status': status,
            'time': e.get('time', '')
        })
        
        if 'Sent' in status:
            counts['Enviado'] += 1
        if 'Opened' in status:
            counts['Entregado/Abierto'] += 1
        if 'Clicked' in status:
            counts['Clic'] += 1
            details_by_dept[dept]['clicked'] += 1
            vulnerable_users.append({'email': email, 'action': 'Clic', 'dept': dept})
        if 'Submitted' in status:
            counts['Credenciales'] += 1
            details_by_dept[dept]['submitted'] += 1
            vulnerable_users.append({'email': email, 'action': 'Credenciales', 'dept': dept})
        if 'Reported' in status:
            counts['Reportado'] += 1

    # Generar gráficas mejoradas
    plt.style.use('dark_background')
    
    # Gráfica principal (pie chart)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    fig.patch.set_facecolor('#0b0e14')
    
    labels = list(counts.keys())
    values = [counts[k] for k in labels]
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    
    wedges, texts, autotexts = ax1.pie(values, labels=labels, autopct='%1.1f%%', 
                                       colors=colors, startangle=90)
    ax1.set_title('Resultados Generales de la Campaña', fontsize=16, color='white', pad=20)
    
    # Gráfica por departamento
    depts = list(details_by_dept.keys())
    dept_totals = [details_by_dept[d]['total'] for d in depts]
    dept_vulnerable = [details_by_dept[d]['clicked'] + details_by_dept[d]['submitted'] for d in depts]
    
    x = range(len(depts))
    width = 0.35
    
    ax2.bar([i - width/2 for i in x], dept_totals, width, label='Total', color='#374151')
    ax2.bar([i + width/2 for i in x], dept_vulnerable, width, label='Vulnerables', color='#ef4444')
    
    ax2.set_xlabel('Departamentos', color='white')
    ax2.set_ylabel('Número de Usuarios', color='white')
    ax2.set_title('Vulnerabilidad por Departamento', color='white')
    ax2.set_xticks(x)
    ax2.set_xticklabels(depts, color='white')
    ax2.legend()
    ax2.tick_params(colors='white')
    
    plt.tight_layout()
    pie_path = os.path.join(OUT, f"campaign_{CID}_analysis.png")
    plt.savefig(pie_path, bbox_inches='tight', facecolor='#0b0e14', dpi=300)
    plt.close()

    # Generar PDF mejorado
    pdf_path = os.path.join(OUT, f"campaign_{CID}_report.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    W, H = A4

    # Página 1: Resumen ejecutivo
    c.setFillColor(HexColor('#1f2937'))
    c.rect(0, H-4*cm, W, 4*cm, fill=1)
    
    c.setFillColor(HexColor('#ffffff'))
    c.setFont("Helvetica-Bold", 20)
    c.drawString(2*cm, H-2*cm, f"Reporte de Campaña de Phishing")
    
    c.setFont("Helvetica", 12)
    c.drawString(2*cm, H-2.8*cm, f"Campaña: {campaign_name}")
    c.drawString(2*cm, H-3.2*cm, f"ID: {CID}")
    c.drawString(2*cm, H-3.6*cm, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    # Resumen de resultados
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, H-5*cm, "📊 Resumen de Resultados")
    
    c.setFont("Helvetica", 11)
    y = H-6*cm
    total_targets = len(results)
    success_rate = ((counts['Clic'] + counts['Credenciales']) / total_targets * 100) if total_targets > 0 else 0
    
    summary_data = [
        f"• Total de objetivos: {total_targets}",
        f"• Emails enviados: {counts['Enviado']} ({counts['Enviado']/total_targets*100:.1f}%)",
        f"• Emails abiertos: {counts['Entregado/Abierto']} ({counts['Entregado/Abierto']/total_targets*100:.1f}%)",
        f"• Clics en enlace: {counts['Clic']} ({counts['Clic']/total_targets*100:.1f}%)",
        f"• Credenciales capturadas: {counts['Credenciales']} ({counts['Credenciales']/total_targets*100:.1f}%)",
        f"• Reportes de phishing: {counts['Reportado']} ({counts['Reportado']/total_targets*100:.1f}%)",
        f"• Tasa de éxito del ataque: {success_rate:.1f}%"
    ]
    
    for item in summary_data:
        c.drawString(2*cm, y, item)
        y -= 0.6*cm

    # Análisis por departamento
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y-0.5*cm, "🏢 Análisis por Departamento")
    y -= 1.2*cm
    
    c.setFont("Helvetica", 11)
    for dept, data in details_by_dept.items():
        if data['total'] > 0:
            vulnerable = data['clicked'] + data['submitted']
            risk_level = "ALTO" if vulnerable/data['total'] > 0.5 else "MEDIO" if vulnerable/data['total'] > 0.2 else "BAJO"
            c.drawString(2*cm, y, f"• {dept}: {vulnerable}/{data['total']} vulnerables ({vulnerable/data['total']*100:.1f}%) - Riesgo {risk_level}")
            y -= 0.6*cm

    # Insertar gráfica
    if os.path.exists(pie_path):
        c.drawImage(pie_path, 2*cm, 2*cm, width=16*cm, height=8*cm, preserveAspectRatio=True, mask='auto')

    # Página 2: Detalles de usuarios vulnerables
    c.showPage()
    
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, H-2*cm, "⚠️ Usuarios Vulnerables - Acción Requerida")
    
    if vulnerable_users:
        c.setFont("Helvetica", 10)
        y = H-3*cm
        
        c.drawString(2*cm, y, "Los siguientes usuarios requieren capacitación adicional en seguridad:")
        y -= 1*cm
        
        for user in vulnerable_users:
            risk_color = HexColor('#ef4444') if user['action'] == 'Credenciales' else HexColor('#f59e0b')
            c.setFillColor(risk_color)
            c.drawString(2*cm, y, f"• {user['email']} ({user['dept']}) - {user['action']}")
            y -= 0.5*cm
            
            if y < 3*cm:
                c.showPage()
                y = H-2*cm
    else:
        c.setFont("Helvetica", 12)
        c.setFillColor(HexColor('#10b981'))
        c.drawString(2*cm, H-4*cm, "✅ ¡Excelente! Ningún usuario cayó en el ataque de phishing.")

    # Página 3: Recomendaciones
    c.showPage()
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, H-2*cm, "💡 Recomendaciones de Seguridad")
    
    recommendations = [
        "1. Capacitación Inmediata:",
        "   • Programar sesión de concientización para usuarios vulnerables",
        "   • Enfatizar en identificación de emails sospechosos",
        "   • Práctica de verificación de enlaces antes de hacer clic",
        "",
        "2. Medidas Técnicas:",
        "   • Implementar filtros de email más estrictos",
        "   • Configurar alertas de seguridad automáticas",
        "   • Considerar autenticación de dos factores",
        "",
        "3. Políticas Organizacionales:",
        "   • Establecer protocolo de reporte de phishing",
        "   • Crear canal de comunicación seguro para dudas",
        "   • Realizar campañas de prueba regulares",
        "",
        "4. Seguimiento:",
        "   • Repetir prueba en 3 meses",
        "   • Monitorear mejoras por departamento",
        "   • Documentar progreso en capacitación"
    ]
    
    c.setFont("Helvetica", 11)
    y = H-3*cm
    for rec in recommendations:
        if rec.startswith(("1.", "2.", "3.", "4.")):
            c.setFont("Helvetica-Bold", 11)
        else:
            c.setFont("Helvetica", 11)
        
        c.drawString(2*cm, y, rec)
        y -= 0.5*cm
        
        if y < 2*cm:
            c.showPage()
            y = H-2*cm

    c.save()
    print(f"✅ Reporte PDF generado: {pdf_path}")
    print(f"✅ Gráficas generadas: {pie_path}")

except Exception as e:
    print(f"❌ Error generando reporte: {e}")
    import traceback
    traceback.print_exc()