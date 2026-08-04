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

app = FastAPI(title="SnapTool API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
