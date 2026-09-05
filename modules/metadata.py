from PIL import Image, ExifTags
import logging

logger = logging.getLogger("BORDERGUARD_METADATA")

EDITING_SOFTWARE_KEYWORDS = [
    "photoshop", "gimp", "canva", "lightroom", "pixlr", "paint.net",
    "illustrator", "snapseed", "inshot", "picsart", "adobe"
]

def analyze_metadata(image_input):
    """
    Extracts EXIF metadata and flags suspicious editing software tags or missing metadata.
    """
    if isinstance(image_input, str):
        pil_img = Image.open(image_input)
    else:
        pil_img = image_input

    indicators = []
    software_found = None
    exif_present = False

    try:
        exif_data = pil_img._getexif()
        if exif_data:
            exif_present = True
            exif_dict = {}
            for tag_id, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                exif_dict[tag_name] = str(value)

            # Check Software tag
            software = exif_dict.get("Software", "")
            for keyword in EDITING_SOFTWARE_KEYWORDS:
                if keyword in software.lower():
                    software_found = software
                    indicators.append(f"EDITING SOFTWARE DETECTED IN EXIF: '{software}'")
                    break

            # Check ModifyDate vs DateTimeOriginal
            created = exif_dict.get("DateTimeOriginal")
            modified = exif_dict.get("DateTime")
            if created and modified and created != modified:
                indicators.append(f"METADATA TIMESTAMP MISMATCH: Created {created}, Modified {modified}")

        else:
            indicators.append("NO EXIF METADATA: Standard camera headers missing (stripped/re-saved)")

    except Exception as e:
        logger.debug(f"EXIF parsing info: {e}")
        indicators.append("METADATA UNREADABLE OR STRIPPED")

    return {
        "exif_present": exif_present,
        "software_detected": software_found,
        "indicators": indicators
    }
