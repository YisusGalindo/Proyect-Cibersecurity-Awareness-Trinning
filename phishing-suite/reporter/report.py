import os, requests, io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
import matplotlib.pyplot as plt

API = os.getenv('GOPHISH_URL','http://localhost:3333')
KEY = os.getenv('GOPHISH_API_KEY','').strip()
CID = os.getenv('CAMPAIGN_ID','').strip()
OUT = '/out'

headers = {'Authorization': f'Bearer {KEY}'}

r = requests.get(f"{API}/api/campaigns/{CID}", headers=headers)
r.raise_for_status()
data = r.json()
results = data.get('results', [])

counts = {
    'Enviado': 0,
    'Entregado/Abierto': 0,
    'Clic': 0,
    'Credenciales': 0,
    'Reportado': 0
}
for e in results:
    status = e.get('status','')
    if status in ('Email Sent',):
        counts['Enviado'] += 1
    if status in ('Email Opened',):
        counts['Entregado/Abierto'] += 1
    if status in ('Clicked Link',):
        counts['Clic'] += 1
    if status in ('Submitted Data',):
        counts['Credenciales'] += 1
    if status in ('Reported',):
        counts['Reportado'] += 1

labels = list(counts.keys())
values = [counts[k] for k in labels]
plt.figure()
plt.pie(values, labels=labels, autopct='%1.1f%%')
pie_path = os.path.join(OUT, f"campaign_{CID}_pie.png")
plt.savefig(pie_path, bbox_inches='tight')
plt.close()

pdf_path = os.path.join(OUT, f"campaign_{CID}_report.pdf")
c = canvas.Canvas(pdf_path, pagesize=A4)
W, H = A4

c.setFont("Helvetica-Bold", 14)
c.drawString(2*cm, H-2*cm, f"Reporte de Campaña #{CID}")

c.setFont("Helvetica", 10)
c.drawString(2*cm, H-3*cm, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')} ")

y = H-4*cm
for k in labels:
    c.drawString(2*cm, y, f"{k}: {counts[k]}")
    y -= 0.6*cm

c.drawImage(pie_path, 2*cm, 4*cm, width=16*cm, height=10*cm, preserveAspectRatio=True, mask='auto')
c.showPage()

c.setFont("Helvetica-Bold", 12)
c.drawString(2*cm, H-2*cm, "Eventos con Clic o Credenciales")

c.setFont("Helvetica", 9)
y = H-3*cm
for e in results:
    if e.get('status') in ('Clicked Link','Submitted Data'):
        line = f"{e.get('email')}: {e.get('status')} @ {e.get('time','')}"
        c.drawString(2*cm, y, line)
        y -= 0.5*cm
        if y < 3*cm:
            c.showPage(); y = H-2*cm

c.save()
print(f"PDF generado: {pdf_path}")
