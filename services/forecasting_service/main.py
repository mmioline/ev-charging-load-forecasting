from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .processor import predict_next_day, predict_station_idle_probability

app = FastAPI(title="EV-Charging-System Forecasting Service")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/predict/{station_id}") 
def get_prediction(station_id: int):
    result = predict_next_day(station_id)
    idle_probability, idle_message = predict_station_idle_probability(station_id)
    return {
        "station_id": station_id,
        "predicted_load_kwh": result, 
        "idle_probability_next_hour": idle_probability,
        "idle_probability_message": idle_message,
        "model_type": "LSTM (Deep Learning)"
    }
