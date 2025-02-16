import os
from fastapi import FastAPI, File, UploadFile, Query, HTTPException, Response
from rembg import remove, new_session
from io import BytesIO
from PIL import Image
import requests
import uvicorn
import gc

app = FastAPI()

# Initialize rembg session with the smallest model
session = new_session(model_name="u2netp")

def process_image(input_image):
    try:
        # Calculate size for resizing if image is too large
        max_size = 1500  # Reduced from 2000
        orig_width, orig_height = input_image.size
        
        # Resize if image is too large
        if orig_width > max_size or orig_height > max_size:
            ratio = min(max_size/orig_width, max_size/orig_height)
            new_size = (int(orig_width*ratio), int(orig_height*ratio))
            input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Convert to RGB if not already
        if input_image.mode != 'RGB':
            input_image = input_image.convert('RGB')
        
        # Remove background
        output_image = remove(input_image, session=session)
        
        # Clear any references to the input image
        del input_image
        gc.collect()
        
        return output_image
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {
        "message": "Background removal service is running!",
        "model": "u2netp",
        "max_image_dimension": 1500
    }

@app.post("/remove-bg/url/")
async def remove_bg_url(
    imgurl: str = Query(..., description="Image URL to process"),
    size_limit: int = Query(1500, description="Maximum image dimension")
):
    try:
        # Download image with timeout and size limit
        response = requests.get(imgurl, timeout=10, stream=True)
        response.raise_for_status()
        
        # Check content length if available
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(status_code=400, detail="Image too large (max 5MB)")
        
        # Process image in chunks
        content = BytesIO()
        for chunk in response.iter_content(chunk_size=8192):
            content.write(chunk)
        content.seek(0)
        
        input_image = Image.open(content).convert('RGB')
        output_image = process_image(input_image)
        
        # Optimize output
        img_io = BytesIO()
        output_image.save(img_io, format="PNG", optimize=True, compression_level=9)
        img_io.seek(0)
        
        # Clear memory
        del output_image
        gc.collect()
        
        return Response(
            content=img_io.getvalue(),
            media_type="image/png",
            headers={"X-Original-Size": f"{input_image.size[0]}x{input_image.size[1]}"}
        )
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching image: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.post("/remove-bg/file/")
async def remove_bg_file(
    file: UploadFile = File(...),
    size_limit: int = Query(1500, description="Maximum image dimension")
):
    try:
        # Validate file size (5MB limit)
        content = await file.read(5 * 1024 * 1024 + 1)  # Read slightly more than 5MB to check size
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File too large (max 5MB)")
        
        input_image = Image.open(BytesIO(content)).convert('RGB')
        output_image = process_image(input_image)
        
        # Optimize output
        img_io = BytesIO()
        output_image.save(img_io, format="PNG", optimize=True, compression_level=9)
        img_io.seek(0)
        
        # Clear memory
        del output_image
        del input_image
        gc.collect()
        
        return Response(
            content=img_io.getvalue(),
            media_type="image/png",
            headers={"X-Original-Size": f"{input_image.size[0]}x{input_image.size[1]}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on port {port}")
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        workers=1  # Limit to single worker to reduce memory usage
    )