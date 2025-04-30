import streamlit as st
import requests
import openmeteo_requests
import requests_cache
import pandas as pd
import matplotlib.pyplot as plt
from retry_requests import retry

# Setup Open-Meteo API client with caching and retry
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# --- Model ---
def predict_wattage(irradiance_array, temperature_array, num_panels, panel_rating):
    efficiency_factor = 0.75
    wattage_per_panel = irradiance_array * efficiency_factor
    total_wattage = wattage_per_panel * num_panels * (panel_rating / 1000)
    return total_wattage

def get_weather_data(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": [
            "temperature_2m", "relative_humidity_2m", "shortwave_radiation",
            "direct_radiation", "diffuse_radiation", "direct_normal_irradiance",
            "global_tilted_irradiance"
        ],
        "forecast_days": 7  # Request 7 days forecast
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]
    hourly = response.Hourly()

    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
        "direct_radiation": hourly.Variables(3).ValuesAsNumpy()
    }

    df = pd.DataFrame(hourly_data)
    return df

# --- UI Starts Here ---
st.set_page_config(page_title="Solar Output Estimator", page_icon="🔆", layout="centered")
st.title("🔋 Solar Panel Output Estimator")
st.markdown("Forecast the energy output of your solar system for the coming week!")

# --- Sidebar Inputs ---
st.sidebar.header("🛠️ System Configuration")
latitude = st.sidebar.number_input("Latitude", format="%.6f")
longitude = st.sidebar.number_input("Longitude", format="%.6f")
num_panels = st.sidebar.number_input("Number of Panels", min_value=1, step=1)
panel_rating = st.sidebar.number_input("Panel Rating (Watts)", min_value=0)

# --- Prediction Button ---
if st.sidebar.button("⚡ Get Prediction"):
    with st.spinner("Fetching weather data and predicting output..."):
        try:
            weather_df = get_weather_data(latitude, longitude)
            weather_df["predicted_wattage"] = predict_wattage(
                weather_df["direct_radiation"],
                weather_df["temperature_2m"],
                num_panels,
                panel_rating
            )

            st.success("✅ Forecast retrieved successfully!")
            st.subheader("📈 Solar Output Forecast for the Next 7 Days")

            # Plot
            fig, ax1 = plt.subplots(figsize=(12, 6))

            ax1.plot(weather_df["date"], weather_df["predicted_wattage"], label="Predicted Wattage (W)", linewidth=2)
            ax1.plot(weather_df["date"], weather_df["direct_radiation"], label="Irradiance (W/m²)", linestyle='--')
            ax1.set_xlabel("Date and Time")
            ax1.set_ylabel("Power / Irradiance")
            ax1.tick_params(axis='x', rotation=45)
            ax1.legend(loc="upper left")

            ax2 = ax1.twinx()
            ax2.plot(weather_df["date"], weather_df["temperature_2m"], label="Temperature (°C)", color='orange', alpha=0.6)
            ax2.set_ylabel("Temperature (°C)")
            ax2.legend(loc="upper right")

            st.pyplot(fig)

            with st.expander("📊 View Raw Forecast Data"):
                st.dataframe(weather_df.head(50))

        except Exception as e:
            st.error(f"❌ Failed to fetch weather data: {e}")
