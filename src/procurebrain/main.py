from fastapi import FastAPI

from procurebrain.api.router import router


app = FastAPI(title="ProcureBrain", version="0.1.0")
app.include_router(router)
