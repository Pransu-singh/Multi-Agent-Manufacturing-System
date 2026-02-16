from fastapi import FastAPI
from pydantic import BaseModel
from crew import run_crew
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ManufacturingRequest(BaseModel):
    product: str

@app.post("/generate-report")
def generate_report(req: ManufacturingRequest):
    result = run_crew(req.product)
    return {"report": result}
