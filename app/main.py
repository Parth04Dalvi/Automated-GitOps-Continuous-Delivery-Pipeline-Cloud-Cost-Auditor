from fastapi import FastAPI, Response, status

app = FastAPI(title="GitOps Protected Microservice", version="1.0.0")


@app.get("/healthz", status_code=status.HTTP_200_OK)
def health_check():
    return {"status": "healthy", "service": "order-api"}


@app.get("/")
def read_root():
    return {"message": "Serving traffic via GitOps Automated Delivery Pipeline."}
