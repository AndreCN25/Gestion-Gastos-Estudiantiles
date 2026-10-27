from collections import defaultdict
from decimal import Decimal
import httpx
from .config import settings


async def fetch_weather(city: str | None = None, latitude: float | None = None, longitude: float | None = None):
    """Fetch a forecast by city name or exact browser-provided coordinates."""
    async with httpx.AsyncClient(timeout=8) as client:
        place_name = city or "Tu ubicación actual"
        if latitude is None or longitude is None:
            geo = await client.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1, "language": "es", "format": "json"})
            geo.raise_for_status()
            results = geo.json().get("results", [])
            if not results:
                return {"city": city, "message": "No encontramos esa ciudad."}
            place = results[0]
            latitude, longitude = place["latitude"], place["longitude"]
            place_name = place["name"]
        forecast = await client.get("https://api.open-meteo.com/v1/forecast", params={"latitude": latitude, "longitude": longitude, "current": "temperature_2m,weather_code"})
        forecast.raise_for_status()
        current = forecast.json().get("current", {})
        return {"city": place_name, "temperature_c": current.get("temperature_2m"), "weather_code": current.get("weather_code"), "condition": weather_condition(current.get("weather_code"))}


def weather_condition(code: int | None) -> str:
    """Translate Open-Meteo WMO codes into a short Spanish description."""
    conditions = {
        0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Nublado",
        45: "Niebla", 48: "Niebla con escarcha", 51: "Llovizna ligera", 53: "Llovizna moderada",
        55: "Llovizna intensa", 56: "Llovizna helada ligera", 57: "Llovizna helada intensa",
        61: "Lluvia ligera", 63: "Lluvia moderada", 65: "Lluvia intensa", 66: "Lluvia helada ligera",
        67: "Lluvia helada intensa", 71: "Nevada ligera", 73: "Nevada moderada", 75: "Nevada intensa",
        77: "Granos de nieve", 80: "Chubascos ligeros", 81: "Chubascos moderados", 82: "Chubascos intensos",
        85: "Chubascos de nieve ligeros", 86: "Chubascos de nieve intensos", 95: "Tormenta eléctrica",
        96: "Tormenta con granizo ligero", 99: "Tormenta con granizo intenso",
    }
    return conditions.get(code, "Condición no disponible")


async def fetch_exchange(source: str, target: str):
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get("https://api.frankfurter.dev/v2/rates", params={"base": source, "quotes": target})
        response.raise_for_status()
        rates = response.json()
        if not rates:
            return {"date": None, "from": source, "to": target, "rate": None}
        latest = rates[0]
        return {"date": latest.get("date"), "from": source, "to": target, "rate": latest.get("rate")}


async def spending_tips(expenses):
    totals = defaultdict(lambda: Decimal("0.00"))
    for item in expenses:
        totals[item.category] += item.amount
    if not totals:
        return {"tips": "Registra tus primeros gastos para recibir recomendaciones."}
    data = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
    if settings.openai_api_key:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "system", "content": "Eres un asistente educativo de presupuesto. Responde en español en tres consejos breves y respetuosos. No des asesoría financiera profesional ni inventes información."}, {"role": "user", "content": f"Gastos agrupados por categoría (moneda local): {data}"}],
            max_tokens=220,
        )
        return {"tips": response.choices[0].message.content or "Sin recomendaciones por ahora."}
    top = data[0]
    return {"tips": f"Tu categoría con más gasto es {top[0]} (${top[1]:.2f}). Revisa si puedes fijar un límite semanal y registra tus gastos pequeños para tener un panorama completo.", "mode": "reglas locales; configura OPENAI_API_KEY para activar el modelo de lenguaje"}
