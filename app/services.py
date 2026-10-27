from collections import defaultdict
from decimal import Decimal
import httpx
from .config import settings


async def fetch_weather(city: str):
    """Open-Meteo geocoding + forecast; both APIs are free and keyless."""
    async with httpx.AsyncClient(timeout=8) as client:
        geo = await client.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1, "language": "es", "format": "json"})
        geo.raise_for_status()
        results = geo.json().get("results", [])
        if not results:
            return {"city": city, "message": "No encontramos esa ciudad."}
        place = results[0]
        forecast = await client.get("https://api.open-meteo.com/v1/forecast", params={"latitude": place["latitude"], "longitude": place["longitude"], "current": "temperature_2m,weather_code"})
        forecast.raise_for_status()
        current = forecast.json().get("current", {})
        return {"city": place["name"], "temperature_c": current.get("temperature_2m"), "weather_code": current.get("weather_code")}


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
