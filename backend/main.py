from fastapi import FastAPI, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import uuid
import random
import os
from typing import List
import json

# Optional face detection (simple and fast)
try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    OPENCV_AVAILABLE = True
except Exception:
    OPENCV_AVAILABLE = False

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
ASSETS_DIR = BASE_DIR / "assets"
GENERATED_DIR = BASE_DIR / "generated"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

FONT_PATH = ASSETS_DIR / "Anton-Regular.ttf"
DEFAULT_FONT_SIZE = 64

app = FastAPI(
    title="Dirt to Meme Magic",
    description="Upload an image, we detect what's inside and turn it into a meme.",
    version="1.0.0",
)

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Meme-Data"],
)

# Serve generated memes
app.mount("/static", StaticFiles(directory=str(GENERATED_DIR)), name="static")


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.get("/")
def root():
    return {"message": "Dirt to Meme Magic API. POST an image to /upload"}


def detect_faces(pil_img: Image.Image) -> bool:
    if not OPENCV_AVAILABLE:
        return False
    try:
        img = np.array(pil_img.convert("RGB"))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))
        return len(faces) > 0
    except Exception:
        return False


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    words = text.split()
    lines: List[str] = []
    current = ""
    for w in words:
        test = (current + " " + w).strip()
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return "\n".join(lines)


def add_caption(img: Image.Image, text: str) -> Image.Image:
    # Prepare drawing
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # Scale font based on width
    font_size = max(28, int(width * 0.06))
    try:
        font = ImageFont.truetype(str(FONT_PATH), font_size)
    except Exception:
        font = ImageFont.load_default()

    # Uppercase for meme style
    text = text.upper()
    max_text_width = int(width * 0.9)
    text = wrap_text(draw, text, font, max_text_width)

    # Position at top with padding
    lines = text.split("\n")
    line_height = sum(font.getbbox(line)[3] for line in lines) + (len(lines) - 1) * int(font_size * 0.25)
    y = int(height * 0.04)

    # Draw centered with black stroke
    for i, line in enumerate(lines):
        line_w = draw.textlength(line, font=font)
        x = (width - line_w) / 2
        draw.text(
            (x, y),
            line,
            font=font,
            fill=(255, 255, 255),
            stroke_width=max(2, int(font_size * 0.08)),
            stroke_fill=(0, 0, 0),
            align="center",
        )
        y += font.getbbox(line)[3] + int(font_size * 0.25)

    # Subtle footer watermark
    try:
        footer_font = ImageFont.truetype(str(FONT_PATH), max(14, int(width * 0.025)))
    except Exception:
        footer_font = ImageFont.load_default()
    footer = "Dirt to Meme Magic"
    fw = draw.textlength(footer, font=footer_font)
    draw.text(
        ((width - fw) / 2, height - int(width * 0.06)),
        footer,
        font=footer_font,
        fill=(255, 255, 255),
        stroke_width=2,
        stroke_fill=(0, 0, 0),
    )

    return img


def add_template_overlay(img: Image.Image) -> Image.Image:
    # Paste a small decorative template in the corner if available
    try:
        template_files = [p for p in TEMPLATES_DIR.glob("*.*") if p.suffix.lower() in {".png", ".jpg", ".jpeg"}]
        if not template_files:
            return img
        chosen = random.choice(template_files)
        overlay = Image.open(chosen).convert("RGBA")
        # Scale overlay to ~20% of width
        w, h = img.size
        target_w = int(w * 0.22)
        ratio = target_w / overlay.width
        overlay = overlay.resize((target_w, int(overlay.height * ratio)), Image.Resampling.LANCZOS)
        # Reduce opacity
        alpha = overlay.split()[3]
        alpha = alpha.point(lambda p: int(p * 0.6))
        overlay.putalpha(alpha)
        # Paste at bottom-right with margin
        margin = int(w * 0.03)
        img.paste(overlay, (w - overlay.width - margin, h - overlay.height - margin), overlay)
    except Exception:
        return img
    return img


FACE_CAPTIONS = [
    "When you open the front camera by accident",
    "That one friend who says 'trust me'",
    "I was today years old when I realized...",
    "POV: you said you’re 'fine'",
    "When you accidentally hit 'reply all'",
    "That moment you hear someone say your name",
    "Me pretending to listen but actually daydreaming",
    "When you realize tomorrow is Monday",
    "Trying to act normal after sending a risky text",
    "When the teacher says 'this will be on the test'",
]

OBJECT_CAPTIONS = [
    "Me: I'll fix it later. Also me:",
    "When you finally touch grass",
    "Expectation vs. reality",
    "This is fine.",
    "When you try to cook something new",
    "Current mood: buffering",
    "When you find out it’s not all you can eat",
    "How it started vs. how it’s going",
    "When your code runs without errors",
    "Me after one gym session thinking I’m fit now",
]


@app.post("/upload")
async def upload_image(request: Request, file: UploadFile):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a valid image.")

    try:
        content = await file.read()
        pil_img = Image.open(io.BytesIO(content))

        # Ensure it's a format that can be saved as JPEG
        if pil_img.format not in ["JPEG", "PNG", "GIF", "BMP", "WEBP"]:
             raise HTTPException(status_code=400, detail=f"Unsupported image format: {pil_img.format}")

        # Convert to RGB if needed, this handles transparency (RGBA) and palettized (P) images
        if pil_img.mode in ("RGBA", "P"):
            pil_img = pil_img.convert("RGB")
        
        # Resize to a max width/height while preserving aspect
        pil_img.thumbnail((1280, 1280), Image.Resampling.LANCZOS)

        # Simple border for meme framing
        framed = ImageOps.expand(pil_img, border=max(8, pil_img.width // 64), fill=(0, 0, 0))

        # Analysis
        has_face = detect_faces(framed)
        caption = random.choice(FACE_CAPTIONS if has_face else OBJECT_CAPTIONS)

        # Compose
        composed = add_caption(framed, caption)
        composed = add_template_overlay(composed)

        # Save
        out_name = f"{uuid.uuid4().hex}.jpg"
        out_path = GENERATED_DIR / out_name
        composed.save(out_path, format="JPEG", quality=92)

        meme_data = {
            "caption": caption,
            "faceDetected": has_face,
        }
        
        headers = {"X-Meme-Data": json.dumps(meme_data)}
        return FileResponse(out_path, media_type="image/jpeg", headers=headers)

    except HTTPException as e:
        raise e # Re-raise HTTPException
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
