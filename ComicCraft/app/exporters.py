from pathlib import Path
from uuid import uuid4
from fpdf import FPDF
from PIL import Image
from app.config import get_settings

def save_pdf(layout: list[dict], title: str = "ComicCraft") -> str:
    settings = get_settings()
    export_dir = Path(settings.output_dir) / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    filename = f"comic_{uuid4().hex[:10]}.pdf"
    destination = export_dir / filename

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, _latin(title), ln=True, align="C")
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, _latin(f"Panel {panel['panel_number']}: {panel['title']}"), ln=True)

        image_path = Path(settings.output_dir) / panel["image_path"].removeprefix("/static/")
        if image_path.exists():
            with Image.open(image_path) as image:
                width, height = image.size
            max_w, max_h = 180, 110
            ratio = min(max_w / width, max_h / height)
            pdf.image(str(image_path), w=width * ratio, h=height * ratio)
            pdf.ln(5)

        pdf.set_font("Helvetica", "I", 10)
        pdf.multi_cell(0, 6, _latin(panel["scene_description"]))
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 11)
        for label, key in [
            ("Caption", "caption"),
            ("Narration", "narration"),
            ("Dialogue", "dialogue"),
        ]:
            value = panel.get(key, "").strip()
            if value:
                pdf.set_font("Helvetica", "B", 11)
                pdf.write(6, f"{label}: ")
                pdf.set_font("Helvetica", "", 11)
                pdf.multi_cell(0, 6, _latin(value))

    pdf.output(str(destination))
    return f"/static/exports/{filename}"

def _latin(value: str) -> str:
    return value.encode("latin-1", errors="replace").decode("latin-1")
