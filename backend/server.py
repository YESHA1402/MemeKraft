from fastapi import FastAPI, APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone
import shutil
from book_generator import BollywoodBookGenerator
from file_processor import FileProcessor
from document_generator import DocumentGenerator

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Create uploads and outputs directories
UPLOAD_DIR = ROOT_DIR / "uploads"
OUTPUT_DIR = ROOT_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Initialize book generator
book_generator = BollywoodBookGenerator()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Define Models
class BookRequest(BaseModel):
    language: str = "english"
    generation_mode: str = "full"  # "full" or "chapter"
    chapter_number: Optional[int] = None
    chapter_title: Optional[str] = None
    use_uploaded_content: bool = False
    youtube_url: Optional[str] = None

class BookResponse(BaseModel):
    id: str
    status: str
    message: str
    book_id: Optional[str] = None

class ChapterRequest(BaseModel):
    language: str = "english"
    chapter_number: int
    chapter_title: str
    use_uploaded_content: bool = False

class GenerationStatus(BaseModel):
    book_id: str
    status: str
    progress: int
    message: str

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {
        "message": "Bollywood Cloud Computing Book Generator API",
        "version": "1.0.0",
        "endpoints": {
            "upload_slides": "/api/upload/slides",
            "upload_notes": "/api/upload/notes",
            "process_youtube": "/api/youtube/process",
            "generate_book": "/api/generate/book",
            "generate_chapter": "/api/generate/chapter",
            "download": "/api/download/{format}/{book_id}",
            "languages": "/api/languages"
        }
    }

@api_router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    from book_generator import LANGUAGE_CONFIGS
    return {
        "languages": [
            {"code": code, "name": config["name"]}
            for code, config in LANGUAGE_CONFIGS.items()
        ]
    }

@api_router.post("/upload/slides")
async def upload_slides(file: UploadFile = File(...)):
    """Upload lecture slides (PDF/PPT/DOCX)"""
    try:
        file_id = str(uuid.uuid4())
        file_ext = file.filename.split('.')[-1].lower()
        
        if file_ext not in ['pdf', 'pptx', 'docx']:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use PDF, PPTX, or DOCX.")
        
        file_path = UPLOAD_DIR / f"{file_id}.{file_ext}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text
        text_content = FileProcessor.process_file(str(file_path), file_ext)
        
        # Store in database
        doc = {
            "id": file_id,
            "type": "slides",
            "filename": file.filename,
            "file_path": str(file_path),
            "content": text_content[:5000],  # Store first 5000 chars
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.uploads.insert_one(doc)
        
        return {
            "id": file_id,
            "message": "Slides uploaded successfully",
            "filename": file.filename,
            "pages_extracted": len(text_content.split('\n\n'))
        }
    except Exception as e:
        logger.error(f"Error uploading slides: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/upload/notes")
async def upload_notes(file: UploadFile = File(...)):
    """Upload notes (TXT/PDF/DOCX)"""
    try:
        file_id = str(uuid.uuid4())
        file_ext = file.filename.split('.')[-1].lower()
        
        if file_ext not in ['txt', 'pdf', 'docx']:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use TXT, PDF, or DOCX.")
        
        file_path = UPLOAD_DIR / f"{file_id}.{file_ext}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text
        text_content = FileProcessor.process_file(str(file_path), file_ext)
        
        # Store in database
        doc = {
            "id": file_id,
            "type": "notes",
            "filename": file.filename,
            "file_path": str(file_path),
            "content": text_content[:5000],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.uploads.insert_one(doc)
        
        return {
            "id": file_id,
            "message": "Notes uploaded successfully",
            "filename": file.filename,
            "word_count": len(text_content.split())
        }
    except Exception as e:
        logger.error(f"Error uploading notes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/youtube/process")
async def process_youtube(youtube_url: str = Form(...)):
    """Process YouTube video or playlist URL"""
    try:
        transcript = await FileProcessor.get_youtube_transcript(youtube_url)
        
        doc_id = str(uuid.uuid4())
        doc = {
            "id": doc_id,
            "type": "youtube",
            "url": youtube_url,
            "content": transcript[:5000],
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.uploads.insert_one(doc)
        
        return {
            "id": doc_id,
            "message": "YouTube transcript extracted successfully",
            "url": youtube_url,
            "word_count": len(transcript.split())
        }
    except Exception as e:
        logger.error(f"Error processing YouTube: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/generate/book", response_model=BookResponse)
async def generate_book(request: BookRequest):
    """Generate full book"""
    try:
        book_id = str(uuid.uuid4())
        
        # Get user uploaded content if requested
        user_content = ""
        if request.use_uploaded_content:
            uploads = await db.uploads.find({}, {"_id": 0}).to_list(100)
            user_content = "\n\n".join([u.get("content", "") for u in uploads])
        
        if request.youtube_url:
            try:
                transcript = await FileProcessor.get_youtube_transcript(request.youtube_url)
                user_content += "\n\n" + transcript
            except Exception as e:
                logger.warning(f"Could not process YouTube URL: {str(e)}")
        
        # Store generation request
        gen_doc = {
            "book_id": book_id,
            "language": request.language,
            "mode": request.generation_mode,
            "status": "generating",
            "progress": 0,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.generations.insert_one(gen_doc)
        
        # Generate book (async in background ideally, but for MVP doing synchronously)
        logger.info(f"Starting book generation for {book_id}")
        book_data = await book_generator.generate_full_book(
            request.language,
            user_content
        )
        
        # Save book data
        book_doc = {
            "book_id": book_id,
            "language": request.language,
            "data": book_data,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.books.insert_one(book_doc)
        
        # Update status
        await db.generations.update_one(
            {"book_id": book_id},
            {"$set": {"status": "completed", "progress": 100}}
        )
        
        return BookResponse(
            id=str(uuid.uuid4()),
            status="success",
            message="Book generated successfully",
            book_id=book_id
        )
    except Exception as e:
        logger.error(f"Error generating book: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/generate/chapter")
async def generate_chapter(request: ChapterRequest):
    """Generate single chapter"""
    try:
        # Get user uploaded content if requested
        user_content = ""
        if request.use_uploaded_content:
            uploads = await db.uploads.find({}, {"_id": 0}).to_list(100)
            user_content = "\n\n".join([u.get("content", "") for u in uploads])
        
        # Generate chapter
        chapter_content = await book_generator.generate_chapter(
            request.chapter_number,
            request.chapter_title,
            request.language,
            user_content
        )
        
        chapter_id = str(uuid.uuid4())
        chapter_doc = {
            "chapter_id": chapter_id,
            "chapter_number": request.chapter_number,
            "chapter_title": request.chapter_title,
            "language": request.language,
            "content": chapter_content,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.chapters.insert_one(chapter_doc)
        
        return {
            "chapter_id": chapter_id,
            "status": "success",
            "message": "Chapter generated successfully",
            "content": chapter_content
        }
    except Exception as e:
        logger.error(f"Error generating chapter: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/download/{format}/{book_id}")
async def download_book(format: str, book_id: str):
    """Download generated book in specified format"""
    try:
        if format not in ['pdf', 'docx', 'md']:
            raise HTTPException(status_code=400, detail="Format must be pdf, docx, or md")
        
        # Get book data
        book_doc = await db.books.find_one({"book_id": book_id}, {"_id": 0})
        if not book_doc:
            raise HTTPException(status_code=404, detail="Book not found")
        
        book_data = book_doc["data"]
        output_filename = f"bollywood_cloud_book_{book_id}.{format}"
        output_path = OUTPUT_DIR / output_filename
        
        # Generate document
        if format == 'md':
            DocumentGenerator.generate_markdown(book_data, str(output_path))
        elif format == 'docx':
            DocumentGenerator.generate_docx(book_data, str(output_path))
        elif format == 'pdf':
            DocumentGenerator.generate_pdf(book_data, str(output_path))
        
        return FileResponse(
            path=str(output_path),
            filename=output_filename,
            media_type='application/octet-stream'
        )
    except Exception as e:
        logger.error(f"Error downloading book: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/generation/status/{book_id}", response_model=GenerationStatus)
async def get_generation_status(book_id: str):
    """Get book generation status"""
    try:
        gen_doc = await db.generations.find_one({"book_id": book_id}, {"_id": 0})
        if not gen_doc:
            raise HTTPException(status_code=404, detail="Generation not found")
        
        return GenerationStatus(
            book_id=book_id,
            status=gen_doc.get("status", "unknown"),
            progress=gen_doc.get("progress", 0),
            message=f"Generation {gen_doc.get('status', 'in progress')}"
        )
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()