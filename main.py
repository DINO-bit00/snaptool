from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import uuid
import asyncio
import shutil
from pathlib import Path
from typing import List
import zipfile
from fastapi import Form

app = FastAPI(title="SnapTool API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from starlette.middleware.base import BaseHTTPMiddleware
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.endswith(".html") or response.headers.get("content-type") == "text/html":
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheMiddleware)

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

# Pre-load rembg session once at startup (avoids reloading model on every request)
rembg_session = None

@app.on_event("startup")
async def load_rembg():
    global rembg_session
    def _load():
        from rembg import new_session
        return new_session()  # Downloads model on first run, then caches
    loop = asyncio.get_event_loop()
    rembg_session = await loop.run_in_executor(None, _load)
    print("✅ rembg model loaded and ready.")

def get_temp_path(suffix: str) -> Path:
    return TEMP_DIR / f"{uuid.uuid4().hex}{suffix}"

def cleanup(path: Path):
    try:
        if path and path.exists():
            path.unlink()
    except Exception:
        pass


# ─────────────────────────────────────────────
#  API: Remove Background
# ─────────────────────────────────────────────
@app.post("/api/remove-bg")
async def remove_background(file: UploadFile = File(...)):
    allowed = {"image/png", "image/jpeg", "image/webp", "image/jpg"}
    if file.content_type not in allowed:
        raise HTTPException(400, "Only PNG, JPG, and WebP images are supported.")

    input_path = get_temp_path(Path(file.filename).suffix or ".jpg")
    output_path = get_temp_path(".png")

    try:
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        def _run_rembg():
            from rembg import remove
            with open(input_path, "rb") as inp, open(output_path, "wb") as out:
                out.write(remove(inp.read(), session=rembg_session))

        await asyncio.get_event_loop().run_in_executor(None, _run_rembg)

        filename = Path(file.filename).stem + "_no_bg.png"
        return FileResponse(output_path, media_type="image/png", filename=filename)
    except Exception as e:
        cleanup(output_path)
        raise HTTPException(500, f"Background removal failed: {str(e)}")
    finally:
        cleanup(input_path)


# ─────────────────────────────────────────────
#  API: Word → PDF  (cross-platform via docx2pdf or fallback)
# ─────────────────────────────────────────────
@app.post("/api/word-to-pdf")
async def word_to_pdf(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith((".doc", ".docx")):
        raise HTTPException(400, "Only .doc and .docx files are supported.")

    input_path = get_temp_path(".docx")
    output_path = get_temp_path(".pdf")

    try:
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        def _convert():
            import sys
            import subprocess
            
            if sys.platform != "win32":
                # Linux / Render: Use LibreOffice
                subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "pdf",
                     "--outdir", str(output_path.parent), str(input_path)],
                    capture_output=True, timeout=60
                )
                lo_output = output_path.parent / (input_path.stem + ".pdf")
                if lo_output.exists():
                    lo_output.rename(output_path)
                else:
                    raise RuntimeError("LibreOffice conversion failed.")
            else:
                # Windows: Use docx2pdf CLI to avoid COM thread issues
                try:
                    subprocess.run(["docx2pdf", str(input_path), str(output_path)], capture_output=True, timeout=60)
                except Exception as ex:
                    raise RuntimeError(f"docx2pdf failed: {str(ex)}")
                
                if not output_path.exists():
                    raise RuntimeError("Word conversion failed. Make sure Microsoft Word is installed and activated.")

        await asyncio.get_event_loop().run_in_executor(None, _convert)

        if not output_path.exists():
            raise HTTPException(500, "Conversion produced no output.")

        filename = Path(file.filename).stem + ".pdf"
        return FileResponse(output_path, media_type="application/pdf", filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        cleanup(output_path)
        raise HTTPException(500, str(e))
    finally:
        cleanup(input_path)


# ─────────────────────────────────────────────
#  API: PDF → Word
# ─────────────────────────────────────────────
@app.post("/api/pdf-to-word")
async def pdf_to_word(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")

    input_path = get_temp_path(".pdf")
    output_path = get_temp_path(".docx")

    try:
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        def _convert():
            from pdf2docx import Converter
            cv = Converter(str(input_path))
            cv.convert(str(output_path))
            cv.close()

        await asyncio.get_event_loop().run_in_executor(None, _convert)

        filename = Path(file.filename).stem + ".docx"
        return FileResponse(
            output_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=filename,
        )
    except Exception as e:
        cleanup(input_path)
        cleanup(output_path)
        raise HTTPException(500, f"PDF-to-Word conversion failed: {str(e)}")
    finally:
        cleanup(input_path)


# ─────────────────────────────────────────────
#  API: Merge PDF
# ─────────────────────────────────────────────
@app.post("/api/merge-pdf")
async def merge_pdf(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(400, "Please provide at least 2 PDF files to merge.")

    output_path = get_temp_path(".pdf")
    input_paths = []

    try:
        from pypdf import PdfWriter
        
        merger = PdfWriter()
        for file in files:
            if not (file.filename or "").lower().endswith(".pdf"):
                raise HTTPException(400, "All files must be PDFs.")
            temp_path = get_temp_path(".pdf")
            input_paths.append(temp_path)
            with open(temp_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            merger.append(temp_path)
            
        with open(output_path, "wb") as f:
            merger.write(f)
            
        return FileResponse(output_path, media_type="application/pdf", filename="merged.pdf")
    except HTTPException:
        raise
    except Exception as e:
        cleanup(output_path)
        raise HTTPException(500, f"Failed to merge PDFs: {str(e)}")
    finally:
        for p in input_paths:
            cleanup(p)

# ─────────────────────────────────────────────
#  API: Split PDF
# ─────────────────────────────────────────────
def parse_ranges(ranges_str: str, max_pages: int) -> List[List[int]]:
    chunks = []
    for part in ranges_str.split(','):
        part = part.strip()
        if not part: continue
        if '-' in part:
            start_str, end_str = part.split('-', 1)
            try:
                start = max(1, int(start_str))
                end = min(max_pages, int(end_str))
                if start <= end:
                    chunks.append(list(range(start - 1, end)))
            except ValueError:
                continue
        else:
            try:
                p = int(part)
                if 1 <= p <= max_pages:
                    chunks.append([p - 1])
            except ValueError:
                continue
    return chunks

@app.post("/api/split-pdf")
async def split_pdf(file: UploadFile = File(...), ranges: str = Form(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "File must be a PDF.")

    input_path = get_temp_path(".pdf")
    zip_path = get_temp_path(".zip")
    
    try:
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        from pypdf import PdfReader, PdfWriter
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        
        chunks = parse_ranges(ranges, total_pages)
        if not chunks:
            raise HTTPException(400, "Invalid page ranges or ranges out of bounds.")
            
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, chunk in enumerate(chunks):
                writer = PdfWriter()
                for page_num in chunk:
                    writer.add_page(reader.pages[page_num])
                
                chunk_path = get_temp_path(f"_part{i+1}.pdf")
                with open(chunk_path, "wb") as out_f:
                    writer.write(out_f)
                
                zipf.write(chunk_path, arcname=f"split_part_{i+1}.pdf")
                cleanup(chunk_path)
                
        return FileResponse(zip_path, media_type="application/zip", filename=f"{Path(file.filename).stem}_split.zip")
    except HTTPException:
        raise
    except Exception as e:
        cleanup(zip_path)
        raise HTTPException(500, f"Failed to split PDF: {str(e)}")
    finally:
        cleanup(input_path)

# ─────────────────────────────────────────────
#  API: Merge Word
# ─────────────────────────────────────────────
@app.post("/api/merge-word")
async def merge_word(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(400, "Please provide at least 2 Word documents to merge.")

    output_path = get_temp_path(".docx")
    input_paths = []

    try:
        from docx import Document
        from docxcompose.composer import Composer
        
        for file in files:
            if not (file.filename or "").lower().endswith((".doc", ".docx")):
                raise HTTPException(400, "All files must be Word documents (.docx).")
            temp_path = get_temp_path(".docx")
            input_paths.append(temp_path)
            with open(temp_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
                
        def _merge():
            master = Document(input_paths[0])
            composer = Composer(master)
            for p in input_paths[1:]:
                doc = Document(p)
                composer.append(doc)
            composer.save(output_path)

        await asyncio.get_event_loop().run_in_executor(None, _merge)
        return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename="merged.docx")
    except HTTPException:
        raise
    except Exception as e:
        cleanup(output_path)
        raise HTTPException(500, f"Failed to merge Word documents: {str(e)}")
    finally:
        for p in input_paths:
            cleanup(p)

# ─────────────────────────────────────────────
#  API: Split Word (via PDF conversion)
# ─────────────────────────────────────────────
@app.post("/api/split-word")
async def split_word(file: UploadFile = File(...), ranges: str = Form(...)):
    if not (file.filename or "").lower().endswith((".doc", ".docx")):
        raise HTTPException(400, "File must be a Word document.")

    input_path = get_temp_path(".docx")
    pdf_path = get_temp_path(".pdf")
    zip_path = get_temp_path(".zip")
    
    try:
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # 1. Convert DOCX to PDF
        def _convert():
            import sys, subprocess
            if sys.platform != "win32":
                subprocess.run(
                    ["libreoffice", "--headless", "--convert-to", "pdf",
                     "--outdir", str(pdf_path.parent), str(input_path)],
                    capture_output=True, timeout=60
                )
                lo_output = pdf_path.parent / (input_path.stem + ".pdf")
                if lo_output.exists():
                    lo_output.rename(pdf_path)
                else:
                    raise RuntimeError("LibreOffice conversion failed.")
            else:
                try:
                    subprocess.run(["docx2pdf", str(input_path), str(pdf_path)], capture_output=True, timeout=60)
                except Exception as ex:
                    raise RuntimeError(f"docx2pdf failed: {str(ex)}")
                if not pdf_path.exists():
                    raise RuntimeError("Word conversion failed.")

        await asyncio.get_event_loop().run_in_executor(None, _convert)

        # 2. Split the PDF
        from pypdf import PdfReader, PdfWriter
        reader = PdfReader(pdf_path)
        total_pages = len(reader.pages)
        
        chunks = parse_ranges(ranges, total_pages)
        if not chunks:
            raise HTTPException(400, "Invalid page ranges or ranges out of bounds.")
            
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, chunk in enumerate(chunks):
                writer = PdfWriter()
                for page_num in chunk:
                    writer.add_page(reader.pages[page_num])
                
                chunk_path = get_temp_path(f"_part{i+1}.pdf")
                with open(chunk_path, "wb") as out_f:
                    writer.write(out_f)
                
                zipf.write(chunk_path, arcname=f"split_part_{i+1}.pdf")
                cleanup(chunk_path)
                
        return FileResponse(zip_path, media_type="application/zip", filename=f"{Path(file.filename).stem}_split_pdf.zip")
    except HTTPException:
        raise
    except Exception as e:
        cleanup(zip_path)
        raise HTTPException(500, f"Failed to split Word document: {str(e)}")
    finally:
        cleanup(input_path)
        cleanup(pdf_path)


# ─────────────────────────────────────────────
#  API: Image to PDF
# ─────────────────────────────────────────────
MAX_IMG_PDF = 30  # optimal: enough files without overloading browser RAM
ALLOWED_IMG = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff", "image/gif"}

# A4 dimensions in pixels at 96 DPI
A4_W_PT = 595
A4_H_PT = 842


# ─────────────────────────────────────────────
#  API: PDF → MD (Markdown)
# ─────────────────────────────────────────────
@app.post("/api/pdf-to-md")
async def pdf_to_md(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")

    input_path = get_temp_path(".pdf")
    output_path = get_temp_path(".md")

    try:
        with open(input_path, "wb") as f:
            f.write(await file.read())

        def _convert():
            import pymupdf4llm
            md_text = pymupdf4llm.to_markdown(str(input_path))
            with open(output_path, "w", encoding="utf-8") as out_f:
                out_f.write(md_text)

        import asyncio
        await asyncio.get_event_loop().run_in_executor(None, _convert)

        if not output_path.exists():
            raise HTTPException(500, "Conversion produced no output.")

        filename = Path(file.filename).stem + ".md"
        return FileResponse(output_path, media_type="text/markdown", filename=filename)
    except Exception as e:
        cleanup(output_path)
        raise HTTPException(500, f"Failed to convert PDF to Markdown: {str(e)}")
    finally:
        cleanup(input_path)

@app.post("/api/img-to-pdf")
async def img_to_pdf(
    files: List[UploadFile] = File(...),
    layout: str = Form("auto"),  # 'auto' | 'portrait' | 'landscape'
):
    if not files:
        raise HTTPException(400, "No images provided.")
    if len(files) > MAX_IMG_PDF:
        raise HTTPException(400, f"Maximum {MAX_IMG_PDF} images allowed per conversion.")

    input_paths = []
    output_path = get_temp_path(".pdf")

    try:
        from PIL import Image as PILImage

        pil_images = []
        for f in files:
            if f.content_type not in ALLOWED_IMG:
                raise HTTPException(400, f"Unsupported file type: {f.content_type}. Use JPG, PNG, WebP, BMP, TIFF, or GIF.")
            tmp = get_temp_path(".img")
            input_paths.append(tmp)
            with open(tmp, "wb") as out:
                shutil.copyfileobj(f.file, out)

            img = PILImage.open(tmp).convert("RGB")

            # Determine orientation
            if layout == "portrait":
                use_landscape = False
            elif layout == "landscape":
                use_landscape = True
            else:  # auto: follow the image's own orientation
                use_landscape = img.width > img.height

            if use_landscape:
                page_w, page_h = A4_H_PT, A4_W_PT  # swap for landscape
            else:
                page_w, page_h = A4_W_PT, A4_H_PT

            # Scale image to fit A4, preserving aspect ratio
            img_ratio = img.width / img.height
            page_ratio = page_w / page_h
            if img_ratio > page_ratio:
                new_w = page_w
                new_h = int(page_w / img_ratio)
            else:
                new_h = page_h
                new_w = int(page_h * img_ratio)

            resized = img.resize((new_w, new_h), PILImage.LANCZOS)

            # Paste centered on white A4 canvas
            canvas = PILImage.new("RGB", (page_w, page_h), (255, 255, 255))
            offset_x = (page_w - new_w) // 2
            offset_y = (page_h - new_h) // 2
            canvas.paste(resized, (offset_x, offset_y))
            pil_images.append(canvas)

        if not pil_images:
            raise HTTPException(400, "No valid images could be processed.")

        def _save():
            pil_images[0].save(
                output_path,
                format="PDF",
                save_all=True,
                append_images=pil_images[1:],
                resolution=96,
            )

        await asyncio.get_event_loop().run_in_executor(None, _save)
        return FileResponse(output_path, media_type="application/pdf", filename="images_converted.pdf")

    except HTTPException:
        raise
    except Exception as e:
        cleanup(output_path)
        raise HTTPException(500, f"Failed to convert images to PDF: {str(e)}")
    finally:
        for p in input_paths:
            cleanup(p)


# ─────────────────────────────────────────────
#  API: Compress PDF
# ─────────────────────────────────────────────
@app.post("/api/compress-pdf")
async def compress_pdf(mode: str = Form("standard"), file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")
    
    input_path = get_temp_path(".pdf")
    output_path = get_temp_path(".pdf")
    
    try:
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        def _compress():
            import fitz
            doc = fitz.open(input_path)
            
            if mode == "strong":
                new_doc = fitz.open()
                for i in range(len(doc)):
                    page = doc.load_page(i)
                    # Render page to image at lower DPI for strong compression
                    pix = page.get_pixmap(dpi=100)
                    # Convert pixmap to JPEG bytes then wrap as PDF image
                    img_bytes = pix.tobytes("jpeg", jpg_quality=70)
                    # Create a new page in new_doc with same dimensions
                    rect = page.rect
                    new_page = new_doc.new_page(width=rect.width, height=rect.height)
                    new_page.insert_image(rect, stream=img_bytes)
                new_doc.save(output_path, garbage=4, deflate=True)
                new_doc.close()
            else:
                doc.save(output_path, garbage=4, deflate=True, clean=True)
                
            doc.close()
            
        await asyncio.get_event_loop().run_in_executor(None, _compress)
        
        filename = Path(file.filename).stem + "_compressed.pdf"
        return FileResponse(output_path, media_type="application/pdf", filename=filename)
    except Exception as e:
        cleanup(output_path)
        raise HTTPException(500, f"Compression failed: {str(e)}")
    finally:
        cleanup(input_path)

# ─────────────────────────────────────────────
#  API: PDF to Image
# ─────────────────────────────────────────────
@app.post("/api/pdf-to-img")
async def pdf_to_img(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")
    
    input_path = get_temp_path(".pdf")
    zip_path = get_temp_path(".zip")
    
    try:
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        def _extract():
            import fitz
            doc = fitz.open(input_path)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for i in range(len(doc)):
                    page = doc.load_page(i)
                    pix = page.get_pixmap(dpi=150)
                    img_bytes = pix.tobytes("jpeg")
                    zf.writestr(f"page_{i+1}.jpg", img_bytes)
            doc.close()
            
        await asyncio.get_event_loop().run_in_executor(None, _extract)
        
        filename = Path(file.filename).stem + "_images.zip"
        return FileResponse(zip_path, media_type="application/zip", filename=filename)
    except Exception as e:
        cleanup(zip_path)
        raise HTTPException(500, f"Extraction failed: {str(e)}")
    finally:
        cleanup(input_path)

# ─────────────────────────────────────────────
#  API: Protect / Unlock PDF
# ─────────────────────────────────────────────
@app.post("/api/protect-pdf")
async def protect_pdf(password: str = Form(...), file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")
    if not password:
        raise HTTPException(400, "Password is required.")

    input_path = get_temp_path(".pdf")
    output_path = get_temp_path(".pdf")
    
    try:
        from pypdf import PdfWriter, PdfReader
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        def _protect():
            reader = PdfReader(input_path)
            writer = PdfWriter()
            writer.append_pages_from_reader(reader)
            writer.encrypt(password)
            with open(output_path, "wb") as f_out:
                writer.write(f_out)
                
        await asyncio.get_event_loop().run_in_executor(None, _protect)
        
        filename = Path(file.filename).stem + "_protected.pdf"
        return FileResponse(output_path, media_type="application/pdf", filename=filename)
    except Exception as e:
        cleanup(output_path)
        raise HTTPException(500, f"Protection failed: {str(e)}")
    finally:
        cleanup(input_path)

@app.post("/api/unlock-pdf")
async def unlock_pdf(password: str = Form(...), file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")
    if not password:
        raise HTTPException(400, "Password is required.")

    input_path = get_temp_path(".pdf")
    output_path = get_temp_path(".pdf")
    
    try:
        from pypdf import PdfWriter, PdfReader
        from pypdf.errors import FileNotDecryptedError
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        def _unlock():
            reader = PdfReader(input_path)
            if reader.is_encrypted:
                reader.decrypt(password)
            
            # Will raise FileNotDecryptedError if password is wrong
            writer = PdfWriter()
            writer.append_pages_from_reader(reader)
            with open(output_path, "wb") as f_out:
                writer.write(f_out)
                
        await asyncio.get_event_loop().run_in_executor(None, _unlock)
        
        filename = Path(file.filename).stem + "_unlocked.pdf"
        return FileResponse(output_path, media_type="application/pdf", filename=filename)
    except Exception as e:
        cleanup(output_path)
        if "Password is not correct" in str(e) or "FileNotDecryptedError" in str(type(e)):
             raise HTTPException(400, "Incorrect password.")
        raise HTTPException(500, f"Unlock failed: {str(e)}")
    finally:
        cleanup(input_path)


# ─────────────────────────────────────────────
#  Serve static HTML pages
# ─────────────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    return FileResponse("static/index.html")

@app.get("/bg-remover", response_class=HTMLResponse)
async def bg_remover_page():
    return FileResponse("static/bg-remover.html")

@app.get("/word-to-pdf", response_class=HTMLResponse)
async def word_to_pdf_page():
    return FileResponse("static/word-to-pdf.html")

@app.get("/pdf-to-word", response_class=HTMLResponse)
async def pdf_to_word_page():
    return FileResponse("static/pdf-to-word.html")

@app.get("/doc-tools", response_class=HTMLResponse)
async def doc_tools_page():
    return FileResponse("static/doc-tools.html")


@app.get("/pdf-to-md", response_class=HTMLResponse)
async def page_pdf_to_md():
    return FileResponse("static/pdf-to-md.html")
@app.get("/img-to-pdf", response_class=HTMLResponse)
async def img_to_pdf_page():
    return FileResponse("static/img-to-pdf.html")

@app.get("/compress-pdf", response_class=HTMLResponse)
async def compress_pdf_page():
    return FileResponse("static/compress-pdf.html")

@app.get("/pdf-to-img", response_class=HTMLResponse)
async def pdf_to_img_page():
    return FileResponse("static/pdf-to-img.html")

@app.get("/protect-pdf", response_class=HTMLResponse)
async def protect_pdf_page():
    return FileResponse("static/protect-pdf.html")

@app.get("/smart-crop", response_class=HTMLResponse)
async def smart_crop_page():
    return FileResponse("static/smart-crop.html")

@app.post("/api/smart-crop")
async def smart_crop(
    file: UploadFile = File(...),
    ratio: str = Form(...),
    smart_mode: str = Form("true"),
    bg_color: str = Form("none")
):
    try:
        from PIL import Image as PILImage, ImageColor
        import io
        import cv2
        import numpy as np
        
        contents = await file.read()
        
        # 1. Background Removal
        if bg_color.lower() != "none":
            def _run_rembg():
                from rembg import remove
                return remove(contents, session=rembg_session)
            # Remove background using rembg
            contents = await asyncio.get_event_loop().run_in_executor(None, _run_rembg)
            
        img = PILImage.open(io.BytesIO(contents))
        
        # 2. Add Solid Background if requested
        if bg_color.lower() in ["red", "blue"]:
            # Convert color names to hex for standard passport colors
            color_map = {"red": "#db1514", "blue": "#0b00a3"}
            solid_color = color_map.get(bg_color.lower(), bg_color.lower())
            
            # Ensure the image has an alpha channel to use as a mask
            img = img.convert("RGBA")
            bg_img = PILImage.new("RGBA", img.size, solid_color)
            # Paste using alpha channel as mask
            bg_img.paste(img, (0, 0), img)
            img = bg_img

        # Convert to RGB if needed (unless we want to keep it transparent)
        if bg_color.lower() != "transparent" and img.mode in ('RGBA', 'LA'):
            img = img.convert('RGB')
        
        img_w, img_h = img.size
        
        # Parse ratio (e.g., "3:4")
        try:
            rw, rh = map(float, ratio.split(':'))
            target_ratio = rw / rh
        except:
            target_ratio = 1.0 # default square
            
        # Determine maximum possible crop size for this ratio
        if img_w / img_h > target_ratio:
            box_h = img_h
            box_w = int(img_h * target_ratio)
        else:
            box_w = img_w
            box_h = int(img_w / target_ratio)
            
        cx, cy = img_w / 2, img_h / 2
        
        if smart_mode.lower() == "true":
            try:
                # Convert PIL to OpenCV format
                open_cv_image = np.array(img.convert('RGB'))
                open_cv_image = open_cv_image[:, :, ::-1].copy() # RGB to BGR
                gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
                
                # Load Haar Cascade
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                face_cascade = cv2.CascadeClassifier(cascade_path)
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                
                if len(faces) > 0:
                    # Find largest face
                    largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
                    fx, fy, fw, fh = largest_face
                    cx = fx + fw / 2
                    
                    # For portrait ratios (height > width), put eyes around 1/3 from top of crop
                    if target_ratio < 1.0:
                        eyes_y = fy + fh / 3
                        # Ideal top = eyes_y - box_h * 0.33
                        # Therefore center y = top + box_h/2 = eyes_y + box_h * 0.17
                        cy = eyes_y + box_h * 0.17
                    else:
                        cy = fy + fh / 2
            except Exception as e:
                print("Face detection failed, falling back to center crop:", e)
        
        # Ideal top-left
        left = cx - box_w / 2
        top = cy - box_h / 2
        
        # Clamp to image boundaries
        left = max(0, min(left, img_w - box_w))
        top = max(0, min(top, img_h - box_h))
        
        right = left + box_w
        bottom = top + box_h
        
        # Crop
        cropped = img.crop((left, top, right, bottom))
        
        # Output
        out_io = io.BytesIO()
        fmt = "PNG" if (cropped.mode == 'RGBA' or bg_color.lower() == "transparent") else "JPEG"
        if fmt == "JPEG" and cropped.mode == "RGBA":
            cropped = cropped.convert("RGB")
            
        cropped.save(out_io, format=fmt, quality=95)
        out_io.seek(0)
        
        from fastapi.responses import StreamingResponse
        ext = ".png" if fmt == "PNG" else ".jpg"
        out_filename = file.filename.rsplit('.', 1)[0] + "_cropped" + ext
        
        return StreamingResponse(
            out_io,
            media_type=f"image/{fmt.lower()}",
            headers={"Content-Disposition": f'attachment; filename="{out_filename}"'}
        )
    except Exception as e:
        print("Smart crop error:", e)
        return {"error": str(e)}


# ─────────────────────────────────────────────
#  API: AI Image Upscaler
# ─────────────────────────────────────────────
REALESRGAN_DIR = Path("tools/realesrgan")
REALESRGAN_EXE = REALESRGAN_DIR / "realesrgan-ncnn-vulkan.exe"
REALESRGAN_URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesrgan-ncnn-vulkan-20220424-windows.zip"

@app.get("/image-upscaler", response_class=HTMLResponse)
async def image_upscaler_page():
    return FileResponse("static/image-upscaler.html")

@app.post("/api/image-upscaler")
async def image_upscaler(
    file: UploadFile = File(...),
    model: str = Form("general") # "general" or "anime"
):
    if not (file.filename or "").lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        raise HTTPException(400, "Supported formats: JPG, PNG, WebP.")
        
    input_path = get_temp_path(Path(file.filename).suffix or ".jpg")
    output_path = get_temp_path(".png") # Always output as high quality PNG
    
    try:
        with open(input_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        def _upscale():
            import urllib.request
            import zipfile
            import io
            import subprocess
            import time
            
            # Download if not exists
            if not REALESRGAN_EXE.exists():
                print(f"Downloading Real-ESRGAN from {REALESRGAN_URL}...")
                response = urllib.request.urlopen(REALESRGAN_URL)
                zip_data = response.read()
                print("Extracting Real-ESRGAN...")
                # Extract to project root — the ZIP already contains tools/realesrgan/ internally
                with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
                    z.extractall(".")
                print("Real-ESRGAN installed successfully.")
                time.sleep(1) # Ensure files are written
                
            # Determine model flag
            # filenames: realesrgan-x4plus.param / realesrgan-x4plus-anime.param
            model_flag = "realesrgan-x4plus"
            if model == "anime":
                model_flag = "realesrgan-x4plus-anime"
                
            print(f"Running Real-ESRGAN with model {model_flag} on {input_path}...")
            
            # Use full absolute exe path but run with cwd=exe_dir
            # so "-m models" resolves relative to the exe's folder
            exe_abs = str(REALESRGAN_EXE.resolve())
            exe_dir = str(REALESRGAN_EXE.resolve().parent)
            input_abs = str(Path(input_path).resolve())
            output_abs = str(Path(output_path).resolve())
            
            print(f"DEBUG exe_abs: {exe_abs}")
            print(f"DEBUG exe_dir: {exe_dir}")
            print(f"DEBUG input_abs: {input_abs}")
            print(f"DEBUG output_abs: {output_abs}")
            
            cmd = [
                exe_abs,
                "-i", input_abs,
                "-o", output_abs,
                "-n", model_flag,
                "-m", "models",
                "-f", "png"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=exe_dir)
            print(f"DEBUG returncode: {result.returncode}")
            print(f"DEBUG stdout: {result.stdout}")
            print(f"DEBUG stderr: {result.stderr}")
            print(f"DEBUG output exists: {Path(output_abs).exists()}")
            
            # Real-ESRGAN writes GPU info to stderr which can cause non-zero exit;
            # check if output file was actually created instead
            if not Path(output_abs).exists() or Path(output_abs).stat().st_size == 0:
                print(f"Real-ESRGAN Error (rc={result.returncode}): {result.stderr}")
                raise RuntimeError("Failed to process image with Real-ESRGAN.")

        import traceback
        try:
            await asyncio.get_event_loop().run_in_executor(None, _upscale)
        except Exception as inner_e:
            print(f"UPSCALE EXCEPTION: {inner_e}")
            traceback.print_exc()
            raise
        
        filename = Path(file.filename).stem + f"_upscaled_x4.png"
        return FileResponse(output_path, media_type="image/png", filename=filename)
    except Exception as e:
        cleanup(output_path)
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Upscaling failed: {str(e)}")
    finally:
        cleanup(input_path)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
