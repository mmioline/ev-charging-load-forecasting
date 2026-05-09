from fastapi import FastAPI
from .processor import predict_next_day

app = FastAPI(title="EV-Charging-System Forecasting Service")

@app.get("/predict/{station_id}") 
def get_prediction(station_id: int):
    result = predict_next_day(station_id)
    return {
        "station_id": station_id,
        "predicted_load_kwh": result, 
        "model_type": "LSTM (Deep Learning)"
    }