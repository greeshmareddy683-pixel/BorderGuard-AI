import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def generate_synthetic_passport_image(name="JOHNATHAN DOE", passport_num="P1234567", dob="1990-01-01", expiry="2032-05-09", is_tampered=False):
    """
    Generates a realistic synthetic passport graphic for SIH testing.
    """
    width, height = 800, 520
    # Base background: Deep navy header, off-white card body
    img = Image.new('RGB', (width, height), color=(245, 247, 250))
    draw = ImageDraw.Draw(img)

    # Passport Header
    draw.rectangle([0, 0, width, 70], fill=(15, 23, 42))
    draw.text((20, 20), "PASSPORT / PASSEPORT", fill=(56, 189, 248))
    draw.text((650, 20), "REPUBLIC OF UTOPIA", fill=(255, 255, 255))

    # Portrait Box (Simulated Face Photo)
    face_box = [40, 100, 220, 320]
    draw.rectangle(face_box, fill=(210, 220, 230), outline=(30, 41, 59), width=2)
    
    # Draw simple facial features on portrait box
    draw.ellipse([95, 140, 165, 220], fill=(240, 200, 170))  # Head
    draw.ellipse([110, 170, 122, 182], fill=(50, 50, 50))    # Eye L
    draw.ellipse([138, 170, 150, 182], fill=(50, 50, 50))    # Eye R
    draw.line([130, 185, 130, 200], fill=(180, 120, 100), width=2) # Nose
    draw.arc([115, 200, 145, 215], start=0, end=180, fill=(180, 80, 80), width=2) # Smile

    if is_tampered:
        # Add visual tampering artifact around photo region
        draw.rectangle([35, 95, 225, 325], outline=(255, 0, 0), width=3)
        draw.text((45, 330), "[ALTERED PORTRAIT REGION]", fill=(255, 0, 0))

    # Document Fields
    start_x = 260
    fields = [
        ("Type / Type", "P"),
        ("Country Code / Code", "UTO"),
        ("Passport No. / No. Passeport", passport_num),
        ("Surname / Nom", name.split()[-1] if " " in name else name),
        ("Given Names / Prénoms", name.split()[0] if " " in name else ""),
        ("Nationality / Nationalité", "UTO"),
        ("Date of Birth / Date de naissance", dob),
        ("Sex / Sexe", "M"),
        ("Date of Expiry / Date d'expiration", expiry)
    ]

    curr_y = 90
    for label, val in fields:
        draw.text((start_x, curr_y), label, fill=(100, 116, 139))
        draw.text((start_x, curr_y + 14), val, fill=(15, 23, 42))
        curr_y += 36

    # Bottom MRZ Zone (Machine Readable Zone)
    draw.rectangle([0, 420, width, height], fill=(230, 235, 240), outline=(148, 163, 184))
    
    clean_surname = (name.split()[-1] if " " in name else name).replace(" ", "")
    clean_given = (name.split()[0] if " " in name else "").replace(" ", "")
    
    mrz1 = f"P<UTO{clean_surname}<<{clean_given}".ljust(44, '<')
    mrz2 = f"{passport_num:<9}0UTO9001015M3205090<<<<<<<<<<<<<<00"
    
    draw.text((30, 435), mrz1, fill=(15, 23, 42))
    draw.text((30, 465), mrz2, fill=(15, 23, 42))

    return img

def get_demo_scenarios():
    """
    Returns preset test scenarios for SIH judging demos.
    """
    return {
        "SCENARIO_1": {
            "title": "SCENARIO 1 — GENUINE DOCUMENT",
            "description": "Valid passport, verified MRZ, clean image, high face match (Expected: LOW RISK)",
            "doc_name": "JOHNATHAN DOE",
            "doc_num": "P1234567",
            "is_tampered": False,
            "simulated_face_match": 95.8
        },
        "SCENARIO_2": {
            "title": "SCENARIO 2 — TAMPERED DOCUMENT",
            "description": "Passport with altered portrait region, compression ELA anomalies (Expected: HIGH RISK)",
            "doc_name": "VIKTOR KORNEV",
            "doc_num": "J8392014",
            "is_tampered": True,
            "simulated_face_match": 78.0
        },
        "SCENARIO_3": {
            "title": "SCENARIO 3 — IDENTITY FRAUD",
            "description": "Document flagged in Demo Security DB + Biometric face mismatch (Expected: HIGH RISK)",
            "doc_name": "MARIA GONZALEZ",
            "doc_num": "Z9920184",
            "is_tampered": False,
            "simulated_face_match": 34.2
        }
    }
