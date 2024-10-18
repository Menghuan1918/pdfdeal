def strore_pdf(pdf_path, Text):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfbase import pdfmetrics

    c = canvas.Canvas(pdf_path, pagesize=letter)

    pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
    c.setFont("STSong-Light", 12)

    for text in Text:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            c.setFont("STSong-Light", 12)
            c.drawString(100, 750 - i * 13, line)
        c.showPage()
    c.save()
