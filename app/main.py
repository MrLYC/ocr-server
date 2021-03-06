import uvicorn
from fastapi import FastAPI, UploadFile, File
from ddddocr import DdddOcr
from typing import List
from dataclasses import dataclass
import time
from starlette.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI(docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

new_model = DdddOcr(show_ad=False)
old_model = DdddOcr(old=True, show_ad=False)


@dataclass
class ClassificationResult:
    filename: str
    content: str
    cost: float


@dataclass
class OcrHelper:
    model: DdddOcr
    files: List[UploadFile]

    async def classification(self) -> List[ClassificationResult]:
        results: List[ClassificationResult] = []

        for f in self.files:
            image = await f.read()
            start_at = time.time()
            result = self.model.classification(image)
            end_at = time.time()
            results.append(ClassificationResult(f.filename, result, end_at - start_at))
        return results


@app.post("/api/v2/ocr")
async def ocr_v2(files: List[UploadFile] = File(...)) -> List[ClassificationResult]:
    helper = OcrHelper(model=new_model, files=files)
    return await helper.classification()


@app.post("/api/v1/ocr")
async def ocr_v1(files: List[UploadFile] = File(...)) -> List[ClassificationResult]:
    helper = OcrHelper(model=old_model, files=files)
    return await helper.classification()


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="OCR API",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False, debug=False)
