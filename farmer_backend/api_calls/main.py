# data_updater.py
import time
import schedule
from models import my_farmer_db
from dotenv import load_dotenv
import os
import requests
import json
from tools import logger
from api_calls.process import (
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
    compute_soil_protection_recommendations,
    aggregate_hourly_to_daily
)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL", "https://services.cehub.syngenta-ais.com")

endpoints = {
    "short_range_forecast": {
        "path": "/api/Forecast/ShortRangeForecastHourly",
        "params": {
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

def fetch_all_data(id, longitude, latitude):
    """Fetch data from endpoints, compute extra insights, and update the database."""
    results = {}
    # Loop over endpoints (even though it looks like you have one endpoint defined)
    for key, endpoint in endpoints.items():
        url = BASE_URL + endpoint["path"]
        # Copy the default params and update with dynamic coordinates
        params = endpoint.get("params", {}).copy()
        params["longitude"] = longitude
        params["latitude"] = latitude
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            results[key] = response.json()
        except Exception as e:
            logger.error("Error fetching data from %s: %s", url, e)
            results[key] = None

    logger.info(f"Raw results: {results}")

    # Ensure that you aggregate data from the correct key. For example, if your endpoint returns hourly data under key "short_range_forecast":
    hourly_data = results.get("short_range_forecast", [])
    aggregated_data = aggregate_hourly_to_daily(hourly_data)
    
    # Compute extra insights based on the aggregated data.
    extra_data = add_extra_data(aggregated_data)
    # Update the aggregated_data dictionary with the extra insights.
    aggregated_data.update(extra_data)
    
    logger.info(f"Aggregated data with extra insights: {aggregated_data}")

    # Update the database: update if data exists, otherwise insert new data.
    try:
        if my_farmer_db.get_api_data_by_id(id):
            my_farmer_db.update_api_data(id, aggregated_data)
        else:
            my_farmer_db.insert_api_data(id, aggregated_data)
    except Exception as e:
        logger.error("Error updating/inserting data for id %s: %s", id, e)
    
    return aggregated_data


def start_scheduler(id, longitude, latitude):
    """Run the scheduled job in a loop."""
    # For testing, run every 10 seconds (change back to 1 hour for production)
    fetch_all_data(id, longitude, latitude)

    schedule.every(1).hour.do(fetch_all_data, id, longitude, latitude)
    logger.info("Scheduler started with id=%s, longitude=%s, latitude=%s", id, longitude, latitude)
    while True:
        schedule.run_pending()
        time.sleep(1)



