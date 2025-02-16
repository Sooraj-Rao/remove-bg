import os
from fastapi import FastAPI, File, UploadFile, Query, HTTPException, Response
from rembg import remove, new_session
from io import BytesIO
from PIL import Image
import requests
import uvicorn

app = FastAPI()

# Initialize rembg session with the smallest model
session = new_session("u2netp")

def process_image(input_image):
    # Calculate size for resizing if image is too large
    max_size = 2000  # Maximum dimension
    orig_width, orig_height = input_image.size
    
    # Resize if image is too large
    if orig_width > max_size or orig_height > max_size:
        ratio = min(max_size/orig_width, max_size/orig_height)
        new_size = (int(orig_width*ratio), int(orig_height*ratio))
        input_image = input_image.resize(new_size, Image.Resampling.LANCZOS)
    
    # Remove background
    output_image = remove(input_image, session=session)
    
    return output_image

@app.get("/")
def home():
    return {
        "message": "Background removal service is running!",
        "model": "u2netp",
        "max_image_dimension": 2000
    }

@app.post("/remove-bg/url/")
async def remove_bg_url(
    imgurl: str = Query(..., description="Image URL to process"),
    size_limit: int = Query(2000, description="Maximum image dimension")
):
    try:
        # Download image with timeout
        response = requests.get(imgurl, timeout=10)
        response.raise_for_status()
        
        # Open and process image
        input_image = Image.open(BytesIO(response.content)).convert('RGB')
        output_image = process_image(input_image)
        
        # Save and return result
        img_io = BytesIO()
        output_image.save(img_io, format="PNG", optimize=True)
        img_io.seek(0)
        
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
    size_limit: int = Query(2000, description="Maximum image dimension")
):
    try:
        # Validate file size (10MB limit)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(status_code=400, detail="File too large (max 10MB)")
        
        # Process image
        input_image = Image.open(BytesIO(content)).convert('RGB')
        output_image = process_image(input_image)
        
        # Save and return result
        img_io = BytesIO()
        output_image.save(img_io, format="PNG", optimize=True)
        img_io.seek(0)
        
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
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)





# docker build -t my-fastapi-app server/
# docker run -p 8000:8000 my-fastapi-app
