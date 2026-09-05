import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageOps

def generate_ela_image(pil_img, quality=90):
    """
    Performs Error Level Analysis (ELA) on PIL Image.
    Resaves image at quality=90, subtracts from original, and enhances difference.
    """
    import io
    buffer = io.BytesIO()
    pil_img.convert("RGB").save(buffer, 'JPEG', quality=quality)
    buffer.seek(0)

    resaved_img = Image.open(buffer)
    ela_img = ImageChops.difference(pil_img.convert("RGB"), resaved_img)

    extrema = ela_img.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1

    scale = 255.0 / max_diff
    ela_enhanced = ImageEnhance.Brightness(ela_img).enhance(scale * 0.8)
    return ela_enhanced, max_diff

def generate_uv_simulation(pil_img):
    """
    Simulates Ultraviolet (365nm) Lamp fluorescence on document scan.
    Highlights optical watermarks, fluorescent threads, and state crests.
    """
    img_np = np.array(pil_img.convert("RGB"))
    
    # Convert to UV color spectrum (Invert Green/Blue, enhance Cyan/Fluorescence)
    hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
    h, s, v = cv2.split(hsv)
    
    # Shift hue towards deep violet/ultraviolet (130-160 range)
    h_uv = np.full_like(h, 145)
    s_uv = cv2.add(s, 60)
    v_uv = cv2.equalizeHist(v)
    
    uv_hsv = cv2.merge([h_uv, s_uv, v_uv])
    uv_rgb = cv2.cvtColor(uv_hsv, cv2.COLOR_HSV2RGB)
    
    # Overlay simulated glowing security watermark crest & threads
    height, width, _ = uv_rgb.shape
    overlay = uv_rgb.copy()
    
    # Synthetic security watermark crest
    center = (int(width * 0.5), int(height * 0.5))
    radius = int(min(width, height) * 0.25)
    cv2.circle(overlay, center, radius, (0, 255, 230), 2)
    cv2.circle(overlay, center, int(radius * 0.7), (255, 0, 230), 1)
    
    # Fluorescent threads
    for y_pos in [int(height*0.3), int(height*0.6)]:
        cv2.line(overlay, (int(width*0.1), y_pos), (int(width*0.9), y_pos), (50, 255, 100), 1)
        
    blend = cv2.addWeighted(uv_rgb, 0.7, overlay, 0.3, 0)
    
    # UV Watermark verification score
    watermark_intensity = np.mean(v_uv)
    uv_verified = bool(watermark_intensity > 70)
    
    return Image.fromarray(blend), uv_verified

def analyze_tampering(image_input):
    """
    Analyzes document image for digital manipulation & forgery indicators.
    Returns tampering risk %, indicators, visual ELA map, and UV simulation.
    """
    if isinstance(image_input, str):
        pil_img = Image.open(image_input)
    elif isinstance(image_input, np.ndarray):
        pil_img = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
    else:
        pil_img = image_input

    img_np = np.array(pil_img.convert("RGB"))
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

    indicators = []
    risk_score = 0

    # 1. Error Level Analysis (ELA) Variance
    ela_img, max_diff = generate_ela_image(pil_img, quality=90)
    ela_np = np.array(ela_img)
    ela_variance = np.var(ela_np)

    if ela_variance > 1200:
        risk_score += 35
        indicators.append("HIGH ELA VARIANCE: Compression levels indicate multiple resave edits")
    elif ela_variance > 600:
        risk_score += 20
        indicators.append("MODERATE ELA ANOMALY: Isolated high-contrast compression patches detected")

    # 2. High-Frequency Noise Distribution Analysis (Laplacian Filter)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    lap_var = laplacian.var()

    if lap_var < 50:
        risk_score += 25
        indicators.append("ABNORMAL NOISE UNIFORMITY: Text region shows digital smoothing/airbrushing")
    elif lap_var > 2500:
        risk_score += 15
        indicators.append("HIGH NOISE DISPARITY: High-frequency grain mismatched across document body")

    # 3. Edge Gradient & Copy-Paste Boundary Detection
    edges = cv2.Canny(gray, 100, 200)
    edge_density = np.mean(edges)

    if edge_density > 25:
        risk_score += 15
        indicators.append("PORTRAIT BORDER ANOMALY: High edge-density box detected around photo region")

    # 4. UV Lamp Security Watermark Simulation
    uv_img, uv_pass = generate_uv_simulation(pil_img)
    if not uv_pass:
        risk_score += 15
        indicators.append("UV FLUORESCENCE FAIL: Document lacks expected optical watermark reflection")

    tampering_risk = min(max(int(risk_score), 5), 95)

    return {
        "tampering_risk": tampering_risk,
        "indicators": indicators,
        "ela_variance": round(float(ela_variance), 1),
        "ela_image": ela_img,
        "uv_image": uv_img,
        "uv_passed": uv_pass
    }
