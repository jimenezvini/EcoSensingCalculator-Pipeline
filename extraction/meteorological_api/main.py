
import os
import requests
from datetime import datetime, timezone

BASE_URL = "https://apitempo.inmet.gov.br"
TOKEN = os.environ["INMET_API_TOKEN"]


def get_latest_weather():
    now = datetime.now(timezone.utc)

    # Última hora fechada
    observation_time = now.replace(
        minute=0,
        second=0,
        microsecond=0
    )

    date = observation_time.strftime("%Y-%m-%d")
    hour = observation_time.strftime("%H00")

    url = (
        f"{BASE_URL}/token/estacao/dados/"
        f"{date}/{hour}/{TOKEN}"
    )

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    data = get_latest_weather()

    print(f"Estações retornadas: {len(data)}")

    for station in data[:5]:
        print(station)
