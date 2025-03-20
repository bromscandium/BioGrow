# data_updater.py
import time
import schedule
from models import my_farmer_db
from dotenv import load_dotenv
import os
import requests
import json
from process import (
    compute_growth_efficiency,
    compute_water_efficiency,
    compute_rainfall_utilization,
    compute_heat_stress_outlook,
    compute_seasonal_water_use_comparison,
    compute_yield_prediction,
    compute_market_price_forecast,
    compute_harvest_timing_recommendation,
    compute_labor_machinery_cost_insights,
    compute_resource_efficiency,
    compute_recommended_biological_products,
    compute_pest_disease_alert,
    compute_frost_risk,
    compute_irrigation_risk,
    compute_soil_protection_recommendations
)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://services.cehub.syngenta-ais.com")

# Example coordinates (you can update these as needed)
longitude = 45
latitude = 7

endpoints = {
    "short_range_forecast": {
        "path": "/api/Forecast/ShortRangeForecastHourly",
        "params": {
            "latitude": latitude,
            "longitude": longitude,
            "supplier": "Meteoblue",
            "top": "50",
            "format": "json",
            "measureLabel": (
                "Temperature_15Min (C);\n"
                "WindSpeed_15Min (m/s);\n"
                "WindDirection_15Min;\n"
                "HumidityRel_15Min (pct);\n"
                "Cloudcover_Hourly (pct);\n"
                "GlobalRadiation_HourlySum (Wh/m2);\n"
                "HumidityRel_Hourly (pct);\n"
                "Precip_HourlySum (mm);\n"
                "PrecipProbability_Hourly (pct);\n"
                "ShowerProbability_Hourly (pct);\n"
                "SnowFraction_Hourly;\n"
                "SunshineDuration_Hourly (min);\n"
                "TempAir_Hourly (C);\n"
                "Visibility_Hourly (m);\n"
                "WindDirection_Hourly (Deg);\n"
                "WindGust_Hourly (m/s);\n"
                "WindSpeed_Hourly (m/s);\n"
                "Soilmoisture_0to10cm_Hourly (vol%);\n"
                "Soiltemperature_0to10cm_Hourly (C);\n"
                "Referenceevapotranspiration_HourlySum (mm);\n"
                "LeafWetnessProbability_Hourly (pct);\n"
                "Cloudcover_DailyAvg (pct);\n"
                "Evapotranspiration_DailySum (mm);\n"
                "GlobalRadiation_DailySum (Wh/m2);\n"
                "HumidityRel_DailyAvg (pct);\n"
                "HumidityRel_DailyMax (pct);\n"
                "HumidityRel_DailyMin (pct);\n"
                "Precip_DailySum (mm);\n"
                "PrecipProbability_Daily (pct);\n"
                "ShowerProbability_DailyMax (pct);\n"
                "SnowFraction_Daily (pct);\n"
                "SunshineDuration_DailySum (min);\n"
                "TempAir_DailyAvg (C);\n"
                "TempAir_DailyMax (C);\n"
                "TempAir_DailyMin (C);\n"
                "ThunderstormProbability_DailyMax (pct);\n"
                "WindDirection_DailyAvg (Deg);\n"
                "WindGust_DailyMax (m/s);\n"
                "WindSpeed_DailyAvg (m/s);\n"
                "WindSpeed_DailyMax (m/s);\n"
                "WindSpeed_DailyMin (m/s);\n"
                "WindDirection_DailyAvg;\n"
                "Soilmoisture_0to10cm_DailyMax (vol%);\n"
                "Soilmoisture_0to10cm_DailyAvg (vol%);\n"
                "Soilmoisture_0to10cm_DailyMin (vol%);\n"
                "Soiltemperature_0to10cm_DailyMax (C);\n"
                "Soiltemperature_0to10cm_DailyAvg (C);\n"
                "Soiltemperature_0to10cm_DailyMin (C);\n"
                "Referenceevapotranspiration_DailySum (mm)"
            ),
            "ApiKey": API_KEY
        }
    },
}

def add_extra_data(sample_daily_data):
    extra_data = {
        "Growth Efficiency": compute_growth_efficiency(sample_daily_data),
        "Water Efficiency": compute_water_efficiency(sample_daily_data),
        "Rainfall Utilization": compute_rainfall_utilization(sample_daily_data),
        "Heat Stress Outlook": compute_heat_stress_outlook(sample_daily_data),
        "Seasonal Water Use Comparison": compute_seasonal_water_use_comparison(sample_daily_data, irrigation_method_data=0.5),
        "Yield Prediction": compute_yield_prediction(sample_daily_data),
        "Market Price Forecast": compute_market_price_forecast(None),
        "Harvest Timing Recommendation": compute_harvest_timing_recommendation(sample_daily_data),
        "Labor & Machinery Cost Insights": compute_labor_machinery_cost_insights("input", "regional"),
        "Resource Efficiency": compute_resource_efficiency(sample_daily_data, irrigation_method_data=0.5),
        "Recommended Biological Products": compute_recommended_biological_products(sample_daily_data),
        "Pest & Disease Alert": compute_pest_disease_alert(sample_daily_data),
        "Frost Risk": compute_frost_risk(sample_daily_data),
        "Irrigation Risk": compute_irrigation_risk(sample_daily_data),
        "Soil Protection Recommendations": compute_soil_protection_recommendations(sample_daily_data)
    }
    return extra_data

def fetch_all_data():
    """Fetch data from endpoints, compute extra insights, and update the database."""
    results = {}
    for key, endpoint in endpoints.items():
        url = BASE_URL + endpoint["path"]
        params = endpoint.get("params", {})
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            results[key] = response.json()
        except Exception as e:
            results[key] = None

    # Compute extra insights based on the fetched data.
    extra_data = add_extra_data(results)
    results.update(extra_data)

    # Update the database: either update or insert the API data.
    if my_farmer_db.get_api_data():
        my_farmer_db.update_api_data(results)
    else:
        my_farmer_db.insert_api_data(results)

    return results

def start_scheduler():
    """Run the scheduled job in a loop."""
    schedule.every(1).hours.do(fetch_all_data)
    while True:
        schedule.run_pending()
        time.sleep(1)
