import easyocr

reader = easyocr.Reader(['en'])

result = reader.readtext(
    r"static/uploads/WhatsApp Image 2026-06-10 at 12.21.51 PM.jpeg"
)

print(result)