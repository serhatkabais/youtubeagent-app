# -*- coding: utf-8 -*-
import os
import re
import sys
import subprocess

# Ensure required libraries are installed
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])

install_package("markdown")
install_package("pypdf")
install_package("reportlab")

import markdown
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

# Paths
EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
WORKSPACE_DIR = r"D:\CODING TOOLS\ANTIGRAVITY\cumali-hoca-odev-final"
MD_PATH = os.path.join(WORKSPACE_DIR, "final_agent_raporu.md")

# HTML Template with Premium Academic Style (The New Yorker / Academic Serif Style)
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Akademik Rapor</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=Playfair+Display:ital,wght@0,600;0,700;1,600&display=swap');
        
        body {{
            font-family: 'Lora', 'Georgia', serif;
            font-size: 11.5pt;
            line-height: 1.6;
            color: #111111;
            margin: 0;
            padding: 3cm 2.5cm 3cm 2.5cm; /* Print margins handled by padding */
            text-align: justify;
        }}
        
        h1 {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 19pt;
            font-weight: 700;
            text-align: center;
            color: #1A365D;
            line-height: 1.3;
            margin-bottom: 25px;
            text-transform: uppercase;
            letter-spacing: -0.01em;
        }}
        
        h2 {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 14pt;
            font-weight: 700;
            color: #1A365D;
            margin-top: 35px;
            margin-bottom: 15px;
            border-bottom: 1px solid #1A365D;
            padding-bottom: 5px;
            page-break-after: avoid;
        }}
        
        h3 {{
            font-family: 'Lora', Georgia, serif;
            font-size: 12pt;
            font-weight: 600;
            color: #2B6CB0;
            margin-top: 25px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }}
        
        p {{
            margin-top: 0;
            margin-bottom: 12px;
            text-indent: 1.5em; /* Academic paragraph indent */
        }}
        
        /* Disable indent for abstract and first paragraph of sections */
        .abstract p, h1 + p, h2 + p, h3 + p, p.no-indent {{
            text-indent: 0;
        }}
        
        .abstract {{
            background-color: #F7FAFC;
            border: 1px solid #E2E8F0;
            padding: 20px;
            margin-bottom: 30px;
            font-style: italic;
        }}
        
        .abstract-title {{
            font-weight: 600;
            font-style: normal;
            margin-bottom: 8px;
            color: #1A365D;
            text-align: center;
        }}
        
        ul, ol {{
            margin-top: 0;
            margin-bottom: 15px;
            padding-left: 25px;
        }}
        
        li {{
            margin-bottom: 6px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 10pt;
            page-break-inside: avoid;
        }}
        
        th {{
            background-color: #F1F5F9;
            color: #1A365D;
            font-weight: 600;
            border-bottom: 2px solid #CBD5E0;
            padding: 10px;
            text-align: left;
        }}
        
        td {{
            border-bottom: 1px solid #E2E8F0;
            padding: 8px 10px;
            vertical-align: top;
        }}
        
        blockquote {{
            margin: 20px 0;
            padding: 15px 20px;
            background-color: #FFF5F5;
            border-left: 4px solid #8B0000;
            font-style: italic;
        }}
        
        code {{
            font-family: 'Consolas', 'Courier New', monospace;
            background-color: #EDF2F7;
            padding: 2px 4px;
            font-size: 9pt;
            border-radius: 3px;
        }}
        
        pre {{
            font-family: 'Consolas', 'Courier New', monospace;
            background-color: #F7FAFC;
            border: 1px solid #E2E8F0;
            padding: 15px;
            font-size: 8.5pt;
            line-height: 1.4;
            overflow-x: auto;
            margin: 20px 0;
            white-space: pre-wrap;
            page-break-inside: avoid;
        }}
        
        .code-title {{
            font-family: 'Playfair Display', Georgia, serif;
            font-size: 12pt;
            font-weight: bold;
            color: #1A365D;
            margin-top: 30px;
            margin-bottom: 5px;
            border-bottom: 2px solid #CBD5E0;
            padding-bottom: 3px;
            page-break-after: avoid;
        }}
        
        img {{
            display: block;
            max-width: 100%;
            height: auto;
            margin: 30px auto;
            border: 1px solid #CBD5E0;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}
        
        /* Print rules */
        @media print {{
            @page {{ margin: 0; }}
            html, body {{
                width: 210mm;
                height: 297mm;
            }}
            .page-break {{
                page-break-before: always;
            }}
        }}
    </style>
</head>
<body>
    {content}
</body>
</html>
"""

def markdown_to_html_body(md_text):
    # Convert markdown to html using python-markdown with tables and extensions
    html = markdown.markdown(md_text, extensions=['tables', 'fenced_code', 'toc'])
    
    # Custom post-processing for academic structure
    # 1. Format abstract block
    abstract_match = re.search(r'\*\*Özet\*\*\s*(.*?)\n\n\*\*Anahtar Kelimeler:\*\*\s*(.*?)\n', html, re.DOTALL)
    if abstract_match:
        abstract_text = abstract_match.group(1).strip()
        keywords_text = abstract_match.group(2).strip()
        
        abstract_html = f"""<div class="abstract">
            <div class="abstract-title">Özet</div>
            <p>{abstract_text}</p>
            <p class="no-indent"><b>Anahtar Kelimeler:</b> {keywords_text}</p>
        </div>"""
        
        # Replace the original abstract block in html
        pattern = r'<p><strong>Özet</strong>.*?<strong>Anahtar Kelimeler:</strong>.*?</p>'
        html = re.sub(pattern, abstract_html, html, flags=re.DOTALL)
    
    # Make sure we clean up any double abstract headers or residues
    html = html.replace("<p><strong>Özet</strong></p>", "")
    html = html.replace("hr /", "div class='page-break'></div") # Replace hr with page-break
    
    return html

def print_html_to_pdf_headless(html_path, pdf_path):
    print(f"Calling Edge to compile {os.path.basename(html_path)} to PDF...")
    cmd = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path
    ]
    subprocess.run(cmd, check=True)
    print(f"Printed PDF to {pdf_path}")

def stamp_page_numbers(input_pdf_path, output_pdf_path):
    print(f"Stamping page numbers onto {os.path.basename(input_pdf_path)}...")
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()
    total_pages = len(reader.pages)
    
    # Generate a temporary PDF in memory containing page numbers
    from io import BytesIO
    number_pdf_buffer = BytesIO()
    c = canvas.Canvas(number_pdf_buffer, pagesize=A4)
    
    for page_num in range(1, total_pages + 1):
        # A4 measurements: 595.27 x 841.89 points
        # Page numbers centered at the bottom
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawCentredString(595.27 / 2.0, 40, str(page_num))
        c.showPage()
    
    c.save()
    number_pdf_buffer.seek(0)
    
    # Merge the page numbers onto the original PDF
    number_reader = PdfReader(number_pdf_buffer)
    
    for i in range(total_pages):
        page = reader.pages[i]
        number_page = number_reader.pages[i]
        page.merge_page(number_page)
        writer.add_page(page)
        
    with open(output_pdf_path, "wb") as out_f:
        writer.write(out_f)
    print(f"Successfully generated page-numbered PDF: {output_pdf_path}")

def get_code_appendix():
    code_html = "<div class='page-break'></div><h2>EKLER</h2><h3>Ek C: Yazılım Kaynak Kodları</h3>"
    
    files_to_append = [
        ("agent.py", "agent.py (Ajan Karar Sınıfı)"),
        ("tools.py", "tools.py (Nitel Analiz Araçları)"),
        ("api_client.py", "api_client.py (LLM API Bağlantı Modülü)"),
        ("app.py", "app.py (Streamlit Kullanıcı Arayüzü)")
    ]
    
    for filename, title in files_to_append:
        path = os.path.join(WORKSPACE_DIR, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                code_content = f.read()
            # Escape HTML characters to display inside pre
            escaped_code = code_content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            code_html += f"<div class='code-title'>{title}</div><pre><code>{escaped_code}</code></pre>"
    return code_html

def main():
    if not os.path.exists(MD_PATH):
        print(f"Markdown file not found at {MD_PATH}")
        sys.exit(1)
        
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()
        
    html_body = markdown_to_html_body(md_text)
    
    # 1. Compile final_agent_raporu.pdf (Only report)
    html_content_only = HTML_TEMPLATE.format(content=html_body)
    temp_html_only = os.path.join(WORKSPACE_DIR, "temp_rapor.html")
    with open(temp_html_only, "w", encoding="utf-8") as f:
        f.write(html_content_only)
        
    temp_pdf_only = os.path.join(WORKSPACE_DIR, "temp_rapor.pdf")
    final_pdf_only = os.path.join(WORKSPACE_DIR, "final_agent_raporu.pdf")
    
    print_html_to_pdf_headless(temp_html_only, temp_pdf_only)
    stamp_page_numbers(temp_pdf_only, final_pdf_only)
    
    # 2. Compile final_agent_raporu_kodlarla.pdf (Report + code appendix)
    html_body_with_code = html_body + get_code_appendix()
    html_content_with_code = HTML_TEMPLATE.format(content=html_body_with_code)
    temp_html_code = os.path.join(WORKSPACE_DIR, "temp_rapor_kodlarla.html")
    with open(temp_html_code, "w", encoding="utf-8") as f:
        f.write(html_content_with_code)
        
    temp_pdf_code = os.path.join(WORKSPACE_DIR, "temp_rapor_kodlarla.pdf")
    final_pdf_code = os.path.join(WORKSPACE_DIR, "final_agent_raporu_kodlarla.pdf")
    
    print_html_to_pdf_headless(temp_html_code, temp_pdf_code)
    stamp_page_numbers(temp_pdf_code, final_pdf_code)
    
    # Cleanup temporary files
    for temp_file in [temp_html_only, temp_pdf_only, temp_html_code, temp_pdf_code]:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    print("ALL REPORTS GENERATED CLEANLY AND SUCCESSFULLY!")

if __name__ == "__main__":
    main()
