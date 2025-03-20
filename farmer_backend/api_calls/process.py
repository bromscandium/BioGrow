def compute_growth_efficiency(daily_data):
    """
    🌱 Growth Efficiency
    Data Source: TempAir_DailyAvg (C), GlobalRadiation_DailySum (Wh/m2),
                 Soilmoisture_0to10cm_DailyAvg (vol%)
    Calculation & Interpretation:
      Compare growth conditions (heat, sunlight, moisture) to historical benchmarks.
    """
    try:
        temp_avg = float(daily_data.get("TempAir_DailyAvg", 0))
        global_rad = float(daily_data.get("GlobalRadiation_DailySum", 0))
        soilmoisture_avg = float(daily_data.get("Soilmoisture_0to10cm_DailyAvg", 0))
    except Exception as e:
        raise ValueError("Missing data for Growth Efficiency") from e

    # Example heuristic: weighted sum normalized to a 0-100 scale.
    score = (temp_avg / 40 * 0.3 + global_rad / 1000 * 0.4 + soilmoisture_avg / 100 * 0.3) * 100
    interpretation = "Above benchmark" if score > 50 else "Below benchmark"
    return {"Growth Efficiency Score": round(score, 1), "Interpretation": interpretation}


def aggregate_hourly_to_daily(hourly_data):
    """
    Convert a list of hourly data dictionaries into a single dictionary
    by averaging the values for each measure label.
    
    Expects each item in hourly_data to have keys:
      - 'measureLabel'
      - 'value'
    """
    aggregated = {}
    counts = {}
    for entry in hourly_data:
        label = entry.get('measureLabel', '').strip()
        value_str = entry.get('value', '0')
        try:
            value = float(value_str)
        except Exception:
            value = 0.0
        # Aggregate the values (summing and counting for average)
        if label in aggregated:
            aggregated[label] += value
            counts[label] += 1
        else:
            aggregated[label] = value
            counts[label] = 1
    # Compute the average for each label
    for label in aggregated:
        aggregated[label] /= counts[label]
    return aggregated


def compute_water_efficiency(daily_data):
    """
    💧 Water Efficiency
    Data Source: Evapotranspiration_DailySum (mm), Precip_DailySum (mm),
                 Soilmoisture_0to10cm_DailyAvg (vol%)
    Calculation & Interpretation:
      Less water use vs. regional average = higher efficiency.
    """
    try:
        evap = float(daily_data.get("Evapotranspiration_DailySum", 0))
        precip = float(daily_data.get("Precip_DailySum", 0))
        soilmoisture_avg = float(daily_data.get("Soilmoisture_0to10cm_DailyAvg", 0))
    except Exception as e:
        raise ValueError("Missing data for Water Efficiency") from e

    # Heuristic: higher ratio of precip to evap, moderated by soil moisture, gives higher efficiency.
    ratio = precip / (evap + 0.1)
    efficiency = ratio * (soilmoisture_avg / 100)
    interpretation = "High efficiency" if efficiency > 1 else "Low efficiency"
    return {"Water Efficiency Score": round(efficiency, 2), "Interpretation": interpretation}


def compute_rainfall_utilization(daily_data):
    """
    🌧 Rainfall Utilization
    Data Source: Precip_DailySum (mm), Soilmoisture_0to10cm_DailyAvg (vol%),
                 Evapotranspiration_DailySum (mm)
    Calculation & Interpretation:
      Forecast rainfall impact on soil moisture and irrigation needs.
    """
    try:
        precip = float(daily_data.get("Precip_DailySum", 0))
        soilmoisture_avg = float(daily_data.get("Soilmoisture_0to10cm_DailyAvg", 0))
        evap = float(daily_data.get("Evapotranspiration_DailySum", 0))
    except Exception as e:
        raise ValueError("Missing data for Rainfall Utilization") from e

    utilization = precip + (soilmoisture_avg / 10) - evap
    interpretation = "Good rainfall utilization" if utilization > 0 else "Poor rainfall utilization"
    return {"Rainfall Utilization Score": round(utilization, 1), "Interpretation": interpretation}


def compute_heat_stress_outlook(daily_data):
    """
    🌡 Heat Stress Outlook
    Data Source: TempAir_DailyMax (C), TempAir_DailyMin (C),
                 HumidityRel_DailyAvg (pct), WindSpeed_DailyAvg (m/s)
    Calculation & Interpretation:
      Predict stress based on upcoming temperature & humidity levels.
    """
    try:
        temp_max = float(daily_data.get("TempAir_DailyMax", 0))
        temp_min = float(daily_data.get("TempAir_DailyMin", 0))
        humidity_avg = float(daily_data.get("HumidityRel_DailyAvg", 0))
        wind_speed_avg = float(daily_data.get("WindSpeed_DailyAvg", 0))
    except Exception as e:
        raise ValueError("Missing data for Heat Stress Outlook") from e

    # Example heuristic: difference in temperature, adjusted by humidity and wind.
    stress = (temp_max - temp_min) * (100 - humidity_avg) / 100 + wind_speed_avg
    interpretation = "High heat stress" if stress > 10 else "Moderate heat stress"
    return {"Heat Stress Outlook Score": round(stress, 1), "Interpretation": interpretation}


def compute_seasonal_water_use_comparison(daily_data, irrigation_method_data=0):
    """
    📉 Seasonal Water Use Comparison
    Data Source: Evapotranspiration_DailySum (mm), Precip_DailySum (mm),
                 Irrigation method data
    Calculation & Interpretation:
      Compare seasonal water use to regional best practices.
    """
    try:
        evap = float(daily_data.get("Evapotranspiration_DailySum", 0))
        precip = float(daily_data.get("Precip_DailySum", 0))
    except Exception as e:
        raise ValueError("Missing data for Seasonal Water Use Comparison") from e

    seasonal_efficiency = precip / (evap + 0.1) - irrigation_method_data
    interpretation = "Efficient" if seasonal_efficiency > 1 else "Inefficient"
    return {"Seasonal Water Use Comparison Score": round(seasonal_efficiency, 2), "Interpretation": interpretation}


def compute_yield_prediction(daily_data):
    """
    🌾 Yield Prediction (Business Insight)
    Data Source: TempAir_DailyAvg (C), GlobalRadiation_DailySum (Wh/m2),
                 Soilmoisture_0to10cm_DailyAvg (vol%)
    Calculation & Interpretation:
      Correlate temperature, moisture, and light availability with crop growth models.
    """
    try:
        temp_avg = float(daily_data.get("TempAir_DailyAvg", 0))
        global_rad = float(daily_data.get("GlobalRadiation_DailySum", 0))
        soilmoisture_avg = float(daily_data.get("Soilmoisture_0to10cm_DailyAvg", 0))
    except Exception as e:
        raise ValueError("Missing data for Yield Prediction") from e

    yield_score = (temp_avg / 40 * 0.4 + global_rad / 1000 * 0.3 + soilmoisture_avg / 100 * 0.3) * 100
    interpretation = "High yield potential" if yield_score > 50 else "Low yield potential"
    return {"Yield Prediction Score": round(yield_score, 1), "Interpretation": interpretation}


def compute_market_price_forecast(external_market_data):
    """
    💰 Market Price Forecast (Business Insight)
    Data Source: External Market Data (Not in API)
    Calculation & Interpretation:
      Use historical price trends to forecast based on estimated harvest time.
    """
    # Placeholder implementation – requires external market data.
    forecast = "Forecast not available" if not external_market_data else "Forecast computed"
    return {"Market Price Forecast": forecast}


def compute_harvest_timing_recommendation(daily_data):
    """
    ⏳ Harvest Timing Recommendation (Business Insight)
    Data Source: TempAir_DailyAvg (C), Precip_DailySum (mm),
                 WindSpeed_DailyAvg (m/s), HumidityRel_DailyAvg (pct)
    Calculation & Interpretation:
      Predict best harvest window based on weather risks.
    """
    try:
        temp_avg = float(daily_data.get("TempAir_DailyAvg", 0))
        precip = float(daily_data.get("Precip_DailySum", 0))
        wind_speed_avg = float(daily_data.get("WindSpeed_DailyAvg", 0))
        humidity_avg = float(daily_data.get("HumidityRel_DailyAvg", 0))
    except Exception as e:
        raise ValueError("Missing data for Harvest Timing Recommendation") from e

    timing_score = (temp_avg / 40) * 3 + (1 - precip / 10) * 3 + (1 - humidity_avg / 100) * 2 + (1 - wind_speed_avg / 10) * 2
    interpretation = "Optimal harvest window" if timing_score > 5 else "Delayed harvest recommended"
    return {"Harvest Timing Recommendation Score": round(timing_score, 2), "Interpretation": interpretation}


def compute_labor_machinery_cost_insights(user_input, regional_data):
    """
    🚜 Labor & Machinery Cost Insights (Business Insight)
    Data Source: User Input + Regional Data
    Calculation & Interpretation:
      Suggest optimal cost-efficiency strategies.
    """
    # Placeholder: combine user input and regional data to compute cost efficiency.
    insights = "Optimal cost strategy recommended" if user_input and regional_data else "Insufficient data"
    return {"Labor & Machinery Cost Insights": insights}


def compute_resource_efficiency(daily_data, irrigation_method_data=0):
    """
    🏭 Resource Efficiency (Business Insight)
    Data Source: Evapotranspiration_DailySum (mm), Irrigation method
    Calculation & Interpretation:
      Compare irrigation method efficiency to reduce costs.
    """
    try:
        evap = float(daily_data.get("Evapotranspiration_DailySum", 0))
        precip = float(daily_data.get("Precip_DailySum", 0))
    except Exception as e:
        raise ValueError("Missing data for Resource Efficiency") from e

    resource_efficiency = precip / (evap + 0.1) - irrigation_method_data
    interpretation = "Efficient resource use" if resource_efficiency > 1 else "Inefficient resource use"
    return {"Resource Efficiency Score": round(resource_efficiency, 2), "Interpretation": interpretation}


def compute_recommended_biological_products(daily_data):
    """
    🛡 Recommended Biological Products (Protection Insight)
    Data Source: TempAir_DailyAvg (C), Precip_DailySum (mm),
                 HumidityRel_DailyAvg (pct), Soilmoisture_0to10cm_DailyAvg (vol%)
    Calculation & Interpretation:
      Determine stressors and suggest appropriate biological products.
    """
    try:
        temp_avg = float(daily_data.get("TempAir_DailyAvg", 0))
        precip = float(daily_data.get("Precip_DailySum", 0))
        humidity_avg = float(daily_data.get("HumidityRel_DailyAvg", 0))
        soilmoisture_avg = float(daily_data.get("Soilmoisture_0to10cm_DailyAvg", 0))
    except Exception as e:
        raise ValueError("Missing data for Recommended Biological Products") from e

    stress_factor = (temp_avg + precip + (100 - humidity_avg) + (100 - soilmoisture_avg)) / 4
    recommendation = "Biological product recommended" if stress_factor > 50 else "No product needed"
    return {"Recommended Biological Products": recommendation}


def compute_pest_disease_alert(daily_data):
    """
    🐛 Pest & Disease Alert (Protection Insight)
    Data Source: TempAir_DailyAvg (C), HumidityRel_DailyAvg (pct),
                 WindSpeed_DailyAvg (m/s), Precip_DailySum (mm)
    Calculation & Interpretation:
      High humidity and low wind = high pest risk.
    """
    try:
        temp_avg = float(daily_data.get("TempAir_DailyAvg", 0))
        humidity_avg = float(daily_data.get("HumidityRel_DailyAvg", 0))
        wind_speed_avg = float(daily_data.get("WindSpeed_DailyAvg", 0))
        precip = float(daily_data.get("Precip_DailySum", 0))
    except Exception as e:
        raise ValueError("Missing data for Pest & Disease Alert") from e

    risk = (humidity_avg / 100) * (1 - wind_speed_avg / 10) + (precip / 10)
    interpretation = "High pest & disease risk" if risk > 1 else "Low pest & disease risk"
    return {"Pest & Disease Alert Score": round(risk, 2), "Interpretation": interpretation}


def compute_frost_risk(daily_data):
    """
    ⚠️ Frost Risk (Protection Insight)
    Data Source: TempAir_DailyMin (C), Cloudcover_DailyAvg (pct),
                 WindSpeed_DailyAvg (m/s)
    Calculation & Interpretation:
      Predict frost likelihood based on forecasted conditions.
    """
    try:
        temp_min = float(daily_data.get("TempAir_DailyMin", 0))
        cloudcover_avg = float(daily_data.get("Cloudcover_DailyAvg", 0))
        wind_speed_avg = float(daily_data.get("WindSpeed_DailyAvg", 0))
    except Exception as e:
        raise ValueError("Missing data for Frost Risk") from e

    risk = (1 if temp_min < 0 else 0) + (cloudcover_avg / 100) + (1 - wind_speed_avg / 10)
    interpretation = "High frost risk" if risk > 1.5 else "Low frost risk"
    return {"Frost Risk Score": round(risk, 2), "Interpretation": interpretation}


def compute_irrigation_risk(daily_data):
    """
    💦 Irrigation Risk (Protection Insight)
    Data Source: Soilmoisture_0to10cm_DailyAvg (vol%), Referenceevapotranspiration_DailySum (mm),
                 Precip_DailySum (mm)
    Calculation & Interpretation:
      Evaluate groundwater irrigation stability and sustainability.
    """
    try:
        soilmoisture_avg = float(daily_data.get("Soilmoisture_0to10cm_DailyAvg", 0))
        ref_evap = float(daily_data.get("Referenceevapotranspiration_DailySum", 0))
        precip = float(daily_data.get("Precip_DailySum", 0))
    except Exception as e:
        raise ValueError("Missing data for Irrigation Risk") from e

    risk = (100 - soilmoisture_avg) + ref_evap * 10 - precip
    interpretation = "High irrigation risk" if risk > 50 else "Low irrigation risk"
    return {"Irrigation Risk Score": round(risk, 2), "Interpretation": interpretation}


def compute_soil_protection_recommendations(daily_data):
    """
    ✅ Soil Protection Recommendations (Protection Insight)
    Data Source: Soilmoisture_0to10cm_DailyAvg (vol%), Soiltemperature_0to10cm_DailyAvg (C),
                 Evapotranspiration_DailySum (mm)
    Calculation & Interpretation:
      Recommend biological soil treatments to improve fertility.
    """
    try:
        soilmoisture_avg = float(daily_data.get("Soilmoisture_0to10cm_DailyAvg", 0))
        soiltemp_avg = float(daily_data.get("Soiltemperature_0to10cm_DailyAvg", 0))
        evap = float(daily_data.get("Evapotranspiration_DailySum", 0))
    except Exception as e:
        raise ValueError("Missing data for Soil Protection Recommendations") from e

    score = (soilmoisture_avg / 100) * 50 + (100 - abs(soiltemp_avg - 20)) + (100 - evap * 10)
    recommendation = "Soil protection measures recommended" if score < 70 else "Soil conditions acceptable"
    return {"Soil Protection Recommendations": recommendation}

