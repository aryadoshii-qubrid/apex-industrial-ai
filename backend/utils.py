import base64
from fpdf import FPDF

def encode_image_to_base64(image_file) -> str:
    """Helper to convert Streamlit/BytesIO image to Base64 string."""
    return base64.b64encode(image_file.getvalue()).decode('utf-8')

def clean_text(text: str) -> str:
    """
    Removes emojis and special characters that crash the PDF generator.
    Only allows standard English characters (Latin-1).
    """
    if not text:
        return ""
    # Encode to latin-1, replacing errors with a question mark, then decode back
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf_report(chat_history):
    """
    Generates a professional PDF report from the chat history.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Apex Industrial AI - Inspection Report", ln=True, align="C")
    pdf.ln(10)
    
    # Content
    pdf.set_font("Arial", size=11)
    
    for msg in chat_history:
        role = msg["role"].upper()
        # FIX: Clean the text before writing to PDF
        content = clean_text(msg["content"])
        
        if role == "USER":
            pdf.set_text_color(100, 100, 100) # Grey for user
            pdf.cell(0, 10, f"OPERATOR: {content}", ln=True)
        else:
            pdf.set_text_color(0, 0, 0) # Black for AI
            pdf.multi_cell(0, 10, f"ANALYSIS: {content}")
            pdf.ln(5)
            
            # Add Metrics if available
            if "usage" in msg and msg["usage"] is not None:
                u = msg["usage"]
                if isinstance(u, dict):
                    tokens = u.get('total_tokens', 0)
                else:
                    tokens = getattr(u, 'total_tokens', 0)

                pdf.set_font("Courier", size=8)
                pdf.cell(0, 5, f"[METRICS: {tokens} Tokens used]", ln=True)
                pdf.set_font("Arial", size=11) # Reset font
        
        pdf.ln(2)

    # Output to bytes
    return pdf.output(dest='S').encode('latin-1')