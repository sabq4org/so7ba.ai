# Generate fixed PDF using Python directly
from weasyprint import HTML, CSS

# Add CSS to force exact page size
extra_css = CSS(string="""
@page { size: 210mm 297mm; margin: 0; }
.cover { height: 297mm !important; overflow: hidden !important; }
.pg { height: 297mm !important; overflow: hidden !important; }
""")

html = HTML(filename='shish_proposal_v4.html')
doc = html.render(stylesheets=[extra_css])
print(f'صفحات: {len(doc.pages)}')
doc.write_pdf('shish_proposal_v4b.pdf')
print('تم!')
