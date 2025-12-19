import qrcode
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, Dict
import uuid
import os

import math

def get_image_dpi(img, fallback=300):
    """
    Returns DPI from image metadata if available,
    otherwise returns fallback.
    """
    dpi = img.info.get("dpi")
    if dpi and isinstance(dpi, tuple):
        return int(dpi[0])
    return fallback


def images_to_pdf(
    image_path_1: str,
    image_path_2: str,
    output_path: str,
    fallback_dpi: int = 300
) -> str:
    """
    Combine two images into a single PDF (2 pages).
    Generates a uniquely named PDF each time.

    Returns: full path to generated PDF
    """

    # os.makedirs(output_dir, exist_ok=True)

    # Open images and ensure RGB (PDF requirement)
    img1 = Image.open(image_path_1).convert("RGB")
    img2 = Image.open(image_path_2).convert("RGB")

    dpi = get_image_dpi(img1, fallback=fallback_dpi)

    # Save as PDF (img1 first page, img2 second page)
    img1.save(
        output_path,
        save_all=True,
        append_images=[img2],
        resolution=dpi
    )

    return output_path


def fill_eye_donor_card_fields(
    template_path: str,
    output_dir: str,
    name: str,
    dob: str,
    address: str,
    ref_no: str,
    phone: str,
    witness_name: str,
    witness_relation: str,
    witness_phone1: str,
    font_path: Optional[str] = None,
    font_size: int = 105,
    color: Tuple[int, int, int] = (10, 70, 80),
    coords: Optional[Dict[str, Tuple[int, int]]] = None,
) -> str:
    """
    Writes donor & witness details onto the eye donor card image.
    Generates a uniquely named output file each time.

    Returns: full path of generated image
    """

    os.makedirs(output_dir, exist_ok=True)

    img = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    if font_path is None:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

    font = ImageFont.truetype(font_path, font_size)

    # Default coordinates (tune once if needed)
    default_coords = {
        "name": (1265,1392), # (150, 160),
        "dob": (4109,1397), # (495, 160),
        "address":(1392,1683),  # (170, 192),
        "ref_no": (1392, 1925),
        "phone": (4560, 1925),

        "witness_name": (1320, 2459),
        "witness_relation": (1441, 2662),
        "witness_phone1": (1271, 2866),
    }

    if coords:
        default_coords.update(coords)

    def put_text(key: str, text: str):
        if text:
            x, y = default_coords[key]
            draw.text((x, y), text.strip(), font=font, fill=color)

    # Donor fields
    put_text("name", name)
    put_text("dob", dob)
    put_text("address", address)
    put_text("ref_no", ref_no)
    put_text("phone", phone)

    # Witness fields
    put_text("witness_name", witness_name)
    put_text("witness_relation", witness_relation)
    put_text("witness_phone1", witness_phone1)

    # Unique output filename
    filename = f"eye_donor_card_back_{uuid.uuid4().hex[:10]}.png"
    output_path = os.path.join(output_dir, filename)

    img.save(output_path, quality=95)
    return output_path



def make_qr_canvas(qr_data: str, box_w: int, box_h: int) -> Image.Image:
    # 1) Generate QR (square) 
    qr = qrcode.QRCode( version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2, ) 
    qr.add_data(qr_data) 
    qr.make(fit=True) 
    qr_img = qr.make_image( fill_color="black", back_color="white" ).convert("RGB") 
    # Resize QR to fit height (square) 
    qr_size = min(box_w, box_h) # 97 
    qr_img = qr_img.resize((qr_size, qr_size), Image.NEAREST) 
    # 2) Create white canvas of exact placeholder size 
    qr_canvas = Image.new("RGB", (box_w, box_h), "white") 
    # Center QR in placeholder 
    offset_x = (box_w - qr_size) // 2 
    offset_y = (box_h - qr_size) // 2 
    qr_canvas.paste(qr_img, (offset_x, offset_y))

    return qr_canvas


def generate_eye_donor_card(
    qr_data: str,
    template_image: str = "template_front.jpg",
    output_dir: str = "output"
) -> str:
    """
    Generate eye donor card image with embedded QR code.

    :param qr_data: Text / URL to encode in QR
    :param template_image: Path to front card template image
    :param output_dir: Directory to save output images
    :return: Path to generated image
    """

    # QR placeholder configuration (from your design)
    QR_POSITION = (2635, 677)      # (x, y)
    QR_BOX_W, QR_BOX_H = 1325, 1188  # placeholder size

    os.makedirs(output_dir, exist_ok=True)

    qr_canvas = make_qr_canvas(qr_data, QR_BOX_W, QR_BOX_H)

    # 3) Load template & paste QR
    card = Image.open(template_image).convert("RGB")
    card.paste(qr_canvas, QR_POSITION)

    # 4) Save output
    filename = f"eye_donor_card_{uuid.uuid4().hex[:8]}.png"
    output_path = os.path.join(output_dir, filename)
    card.save(output_path, format="PNG")

    return output_path
