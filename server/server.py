from fastapi import FastAPI, File, UploadFile, Query, HTTPException, Response
from rembg import remove
from io import BytesIO
from PIL import Image
import requests
import uvicorn

app = FastAPI()

@app.post("/remove-bg/url/")
async def remove_bg_url(imgurl: str = Query(..., description="Image URL to process")):
    try:
        response = requests.get(imgurl)
        response.raise_for_status()
        
        input_image = Image.open(BytesIO(response.content))

        output_image = remove(input_image)

        img_io = BytesIO()
        output_image.save(img_io, format="PNG")
        img_io.seek(0)

        return Response(content=img_io.getvalue(), media_type="image/png")
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching image: {str(e)}")


@app.post("/remove-bg/file/")
async def remove_bg_file(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        input_image = Image.open(BytesIO(image_bytes))

        output_image = remove(input_image)

        img_io = BytesIO()
        output_image.save(img_io, format="PNG")
        img_io.seek(0)

        return Response(content=img_io.getvalue(), media_type="image/png")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
