from fpdf import FPDF
import json
import os

# Usable page width = 210 - 15 - 15 = 180mm
PAGE_WIDTH = 180
LEFT_MARGIN = 15

def safe_text(text):
    if not isinstance(text, str):
        text = str(text)
    text = text.encode('latin-1', 'replace').decode('latin-1')
    words = text.split(' ')
    wrapped = []
    for w in words:
        if len(w) > 15:
            w = ' '.join(w[i:i+15] for i in range(0, len(w), 15))
        wrapped.append(w)
    return ' '.join(wrapped)

class DDRPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(LEFT_MARGIN, 15, LEFT_MARGIN)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 0, 0)
        self.cell(0, 8, "Detailed Diagnostic Report (DDR)", border=False, align="C")
        self.ln(12)
    
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def draw_horizontal_line(pdf):
    pdf.set_draw_color(220, 220, 220)
    pdf.set_line_width(0.2)
    pdf.line(LEFT_MARGIN, pdf.get_y(), LEFT_MARGIN + PAGE_WIDTH, pdf.get_y())
    pdf.ln(3)

def section_title(pdf, title):
    """Render a consistent section title with page-space check."""
    if pdf.get_y() > 250:
        pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(0, 10, safe_text(title), align="L")
    pdf.ln(10)

def check_space(pdf, needed=40):
    """Add a new page if less than 'needed' mm remain."""
    if pdf.get_y() > (297 - 15 - needed):
        pdf.add_page()

def draw_table_row(pdf, col_widths, texts, is_header=False, severity_col=None):
    """Draw a single table row with multi-line support, ensuring columns don't overflow.
    severity_col: index of the severity column for color coding, or None.
    """
    y_start = pdf.get_y()
    x_start = LEFT_MARGIN
    max_y = y_start
    
    # First pass: calculate heights by rendering into temporary cells
    cell_heights = []
    for i, text in enumerate(texts):
        pdf.set_xy(x_start + sum(col_widths[:i]), y_start)
        # Temporarily calculate height
        nb_lines = pdf.multi_cell(col_widths[i], 5, safe_text(text), border=0, split_only=True)
        h = len(nb_lines) * 5
        cell_heights.append(max(h, 8))
    
    row_height = max(cell_heights)
    
    # Check if row fits on page
    if y_start + row_height > 282:
        pdf.add_page()
        y_start = pdf.get_y()
    
    # Second pass: actually draw the cells
    for i, text in enumerate(texts):
        x = x_start + sum(col_widths[:i])
        pdf.set_xy(x, y_start)
        
        fill = False
        if is_header:
            pdf.set_fill_color(50, 50, 50)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 8)
            fill = True
        elif severity_col is not None and i == severity_col:
            sev = text.strip().lower()
            if sev == "high":
                pdf.set_fill_color(244, 67, 54)
                pdf.set_text_color(255, 255, 255)
            elif sev in ("medium", "moderate"):
                pdf.set_fill_color(255, 152, 0)
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.set_fill_color(76, 175, 80)
                pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 8)
            fill = True
        else:
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(0, 0, 0)
        
        # Draw cell background
        pdf.rect(x, y_start, col_widths[i], row_height)
        if fill:
            pdf.rect(x, y_start, col_widths[i], row_height, style='F')
        
        # Draw text inside the cell with padding
        pdf.set_xy(x + 1, y_start + 1)
        pdf.multi_cell(col_widths[i] - 2, 5, safe_text(text))
        
        # Reset colors
        pdf.set_text_color(0, 0, 0)
    
    pdf.set_y(y_start + row_height)


def generate_pdf(report_data, output_pdf, image_dir):
    pdf = DDRPDF()
    pdf.add_page()

    # --- TABLE OF CONTENTS ---
    if report_data.get("Table_of_Contents"):
        section_title(pdf, "TABLE OF CONTENTS")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        for item in report_data["Table_of_Contents"]:
            pdf.cell(PAGE_WIDTH, 6, safe_text(f"  {item}"))
            pdf.ln()
        pdf.ln(5)
        draw_horizontal_line(pdf)

    # --- INTRODUCTION ---
    intro = report_data.get("Introduction")
    if intro:
        section_title(pdf, "SECTION 1: INTRODUCTION")
        for key in ["Background", "Objective", "Scope_of_Work", "Tools_Used"]:
            val = intro.get(key, "Not Available")
            if val and val != "Not Available":
                label = key.replace("_", " ")
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(40, 40, 40)
                pdf.cell(PAGE_WIDTH, 7, safe_text(f"{label}:"))
                pdf.ln()
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(60, 60, 60)
                pdf.multi_cell(PAGE_WIDTH, 6, safe_text(str(val)))
                pdf.ln(2)
        draw_horizontal_line(pdf)

    # --- METADATA ---
    meta = report_data.get("Metadata")
    if meta:
        check_space(pdf, 80)
        section_title(pdf, "SECTION 2: GENERAL INFORMATION")
        pdf.set_fill_color(240, 240, 240)
        for k, v in meta.items():
            formatted_key = str(k).replace("_", " ")
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.set_x(LEFT_MARGIN)
            pdf.cell(60, 7, safe_text(formatted_key), border=1, fill=True)
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(PAGE_WIDTH - 60, 7, safe_text(str(v)), border=1)
            pdf.ln()
        pdf.ln(5)
        draw_horizontal_line(pdf)

    # --- SUMMARY ---
    summary = report_data.get("Summary")
    if summary:
        check_space(pdf, 50)
        section_title(pdf, "INSPECTION SUMMARY")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(PAGE_WIDTH, 7, safe_text(f"Checklists Flagged: {summary.get('Checklists_Flagged', 'N/A')}"))
        pdf.ln()
        pdf.cell(PAGE_WIDTH, 7, safe_text(f"Overall Score: {summary.get('Score_Percentage', 'N/A')}"))
        pdf.ln(8)
        
        stats = summary.get("Condition_Stats", [])
        if stats:
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(PAGE_WIDTH, 7, "Condition Statistics:")
            pdf.ln(8)
            for stat in stats:
                label = stat.get("Label", "")
                value = stat.get("Value", "")
                if label.lower() == "good":
                    pdf.set_fill_color(76, 175, 80)
                    pdf.set_text_color(255, 255, 255)
                elif label.lower() == "moderate":
                    pdf.set_fill_color(255, 152, 0)
                    pdf.set_text_color(255, 255, 255)
                elif label.lower() == "poor":
                    pdf.set_fill_color(244, 67, 54)
                    pdf.set_text_color(255, 255, 255)
                else:
                    pdf.set_fill_color(200, 200, 200)
                    pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_x(LEFT_MARGIN)
                pdf.cell(60, 8, safe_text(f"  {label}: {value}"), fill=True)
                pdf.ln(9)
            pdf.set_text_color(0, 0, 0)
        pdf.ln(3)
        draw_horizontal_line(pdf)

    # --- CHECKLISTS ---
    checklists = report_data.get("Checklists", [])
    if checklists:
        pdf.add_page()
        section_title(pdf, "SECTION 3: INSPECTION CHECKLISTS")

        for category in checklists:
            check_space(pdf, 30)
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(40, 40, 40)
            cat_name = safe_text(category.get("Category_Name", ""))
            score = safe_text(f"Score: {category.get('Score_Percentage', '')}")
            pdf.cell(130, 10, cat_name, align="L")
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(120, 120, 120)
            pdf.cell(PAGE_WIDTH - 130, 10, score, align="R")
            pdf.ln()
            draw_horizontal_line(pdf)
            
            q_width = 130  # question column
            v_width = PAGE_WIDTH - q_width  # value column (50mm)
            
            for item in category.get("Items", []):
                val = str(item.get("Value", "")).strip()
                
                # Color logic
                r, g, b = (245, 245, 245)
                t_r, t_g, t_b = (0, 0, 0)
                
                val_upper = val.upper()
                if val_upper == "YES":
                    r, g, b = (190, 10, 30)
                    t_r, t_g, t_b = (255, 255, 255)
                elif val_upper in ("NO", "GOOD"):
                    r, g, b = (76, 175, 80)
                    t_r, t_g, t_b = (255, 255, 255)
                elif val_upper == "MODERATE" or "TIME" in val_upper:
                    r, g, b = (250, 170, 0)
                    t_r, t_g, t_b = (0, 0, 0)
                elif val_upper == "POOR":
                    r, g, b = (244, 67, 54)
                    t_r, t_g, t_b = (255, 255, 255)
                elif val_upper in ("N/A", "NOT AVAILABLE"):
                    r, g, b = (180, 180, 180)
                    t_r, t_g, t_b = (60, 60, 60)

                check_space(pdf, 12)
                
                # Question side
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(80, 20, 40)
                y_before = pdf.get_y()
                pdf.set_x(LEFT_MARGIN)
                pdf.multi_cell(q_width, 7, safe_text(item.get("Question", "")))
                y_after = pdf.get_y()
                
                row_h = max(y_after - y_before, 7)
                
                # Value cell - positioned within bounds
                pdf.set_xy(LEFT_MARGIN + q_width, y_before)
                pdf.set_fill_color(r, g, b)
                pdf.set_text_color(t_r, t_g, t_b)
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(v_width, row_h, safe_text(val), align="C", fill=True)
                pdf.set_y(y_before + row_h + 1)
                
            pdf.ln(5)

    # --- IMPACTED AREAS & IMAGES ---
    areas = report_data.get("Impacted_Areas", [])
    if areas:
        pdf.add_page()
        section_title(pdf, "AREA-WISE OBSERVATIONS")
        
        for obs in areas:
            check_space(pdf, 50)
            
            area_name = obs.get("Area", "Unknown Area")
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(PAGE_WIDTH, 8, safe_text(f"Area: {area_name}"), align="L")
            pdf.ln()
            
            # Negative Side
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(180, 20, 20)
            pdf.cell(PAGE_WIDTH, 7, "Negative Side (Damage / Seepage):")
            pdf.ln()
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(PAGE_WIDTH, 6, safe_text(str(obs.get("Negative_Side_Inputs", ""))))
            pdf.ln(2)

            # Positive Side
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(20, 130, 20)
            pdf.cell(PAGE_WIDTH, 7, "Positive Side (Probable Cause):")
            pdf.ln()
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.multi_cell(PAGE_WIDTH, 6, safe_text(str(obs.get("Positive_Side_Inputs", ""))))
            
            # Render Normal Images (2-up layout)
            normal_images = obs.get("Normal_Images", [])
            if normal_images:
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(0, 0, 120)
                pdf.cell(PAGE_WIDTH, 6, "Normal Images:")
                pdf.ln(7)
                _render_images_grid(pdf, normal_images, image_dir)
            
            # Render Thermal Images (2-up layout)
            thermal_images = obs.get("Thermal_Images", [])
            if thermal_images:
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 9)
                pdf.set_text_color(180, 0, 0)
                pdf.cell(PAGE_WIDTH, 6, "Thermal Images:")
                pdf.ln(7)
                _render_images_grid(pdf, thermal_images, image_dir)
            
            pdf.ln(5)
            draw_horizontal_line(pdf)

    # --- FINAL SUMMARY TABLE ---
    summary_rows = report_data.get("Final_Summary_Table", [])
    if summary_rows:
        pdf.add_page()
        section_title(pdf, "SECTION 4: SUMMARY TABLE")
        
        # Column widths that fit well: total = 180mm
        col_widths = [32, 45, 43, 18, 42]
        headers_text = ["Impacted Area", "Observed Issue", "Probable Cause", "Severity", "Suggested Remedy"]
        
        # Draw header
        draw_table_row(pdf, col_widths, headers_text, is_header=True)
        
        for row in summary_rows:
            fields = [
                str(row.get("Impacted_Area", "")),
                str(row.get("Observed_Issue", "")),
                str(row.get("Probable_Cause", "")),
                str(row.get("Severity", "")),
                str(row.get("Suggested_Remedy", ""))
            ]
            draw_table_row(pdf, col_widths, fields, severity_col=3)

    # --- OVERALL RECOMMENDATIONS ---
    recs = report_data.get("Overall_Recommendations", [])
    if recs:
        pdf.ln(8)
        check_space(pdf, 60)
        section_title(pdf, "OVERALL RECOMMENDATIONS")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(0, 0, 0)
        for i, rec in enumerate(recs, 1):
            check_space(pdf, 20)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(40, 40, 40)
            pdf.set_x(LEFT_MARGIN)
            pdf.cell(8, 7, f"{i}.")
            pdf.set_font("Helvetica", "", 10)
            pdf.multi_cell(PAGE_WIDTH - 8, 6, safe_text(rec))
            pdf.ln(2)

    # --- LIMITATION AND PRECAUTION ---
    limitation = report_data.get("Limitation_and_Precaution", "")
    if limitation and limitation != "Not Available":
        pdf.ln(5)
        check_space(pdf, 40)
        section_title(pdf, "SECTION 5: LIMITATION AND PRECAUTION NOTE")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(PAGE_WIDTH, 6, safe_text(limitation))

    pdf.output(output_pdf)


def _render_images_grid(pdf, image_list, image_dir):
    """Render images in a 2-column grid to save space and avoid empty pages."""
    img_w = 85  # Each image width
    gap = 10
    col = 0
    row_y = pdf.get_y()
    row_max_h = 0
    
    for img_name in image_list:
        if not img_name or "not available" in img_name.lower():
            continue
        img_basename = os.path.basename(img_name)
        img_path = os.path.join(image_dir, img_basename)
        if not os.path.exists(img_path):
            continue
        
        # Check if we need a new page
        if row_y > 220 and col == 0:
            pdf.add_page()
            row_y = pdf.get_y()
        
        x = LEFT_MARGIN + col * (img_w + gap)
        try:
            # Get image info for aspect ratio
            info = pdf.image(img_path, x=x, y=row_y, w=img_w)
            img_h = (info["h"] / info["w"]) * img_w if info["w"] > 0 else 60
        except Exception:
            img_h = 10
        
        row_max_h = max(row_max_h, img_h)
        col += 1
        if col >= 2:
            col = 0
            row_y += row_max_h + 5
            row_max_h = 0
            pdf.set_y(row_y)
    
    # If we ended on col=1 (odd image), move y down
    if col == 1:
        pdf.set_y(row_y + row_max_h + 5)

