from collections import defaultdict
from decimal import Decimal
import random
import httpx
from .config import settings


async def fetch_weather(city: str | None = None, latitude: float | None = None, longitude: float | None = None):
    """Fetch a forecast by city name or exact browser-provided coordinates."""
    async with httpx.AsyncClient(timeout=15) as client:
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
        if current.get("temperature_2m") is None:
            return {"city": place_name, "temperature_c": None, "message": "El proveedor no devolvió la temperatura actual."}
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


def _local_saving_tip(totals, previous_tips):
    previous = {" ".join(tip.casefold().split()) for tip in previous_tips}
    if totals:
        (category, currency), amount = max(totals.items(), key=lambda item: item[1])
        value = f"{amount:.2f} {currency}"
        openings = [
            f"En tus registros, {category} suma {value}. ",
            f"La categoría {category} concentra {value} de tus gastos anotados. ",
            f"Llevas registrados {value} en {category}. ",
            f"Tus gastos recientes muestran {value} en {category}. ",
        ]
        actions = [
            "Define un límite semanal y revísalo antes de volver a comprar.",
            "Compara dos opciones antes de la próxima compra de ese tipo.",
            "Anota también las compras pequeñas para encontrar posibles ahorros.",
            "Planea esa compra con una lista y un monto máximo.",
            "Revisa si puedes preparar o resolverlo en casa por menos.",
            "Separa lo necesario de lo opcional antes de decidir el siguiente gasto.",
        ]
        options = [opening + action for opening in openings for action in actions]
    else:
        options = [
            "Separa una cantidad pequeña para ahorrar apenas recibas dinero; guardar primero ayuda a mantener el hábito.",
            "Antes de una compra no planeada, espera un día y revisa si todavía la necesitas.",
            "Define una meta concreta de ahorro y divídela en aportaciones semanales alcanzables.",
            "Anota tus gastos pequeños durante una semana y elige uno que puedas reducir.",
            "Compara precios y costos de entrega; el total final puede diferir del precio anunciado.",
            "Prepara una lista antes de comprar víveres para evitar compras de último momento.",
            "Revisa qué servicios no usas y considera cancelar o pausar alguno.",
            "Fija un monto semanal para gastos opcionales después de cubrir tus necesidades.",
            "Si recibes dinero extra, divide una parte entre ahorro y gastos planeados.",
            "Lleva una meta visible, como ahorrar para algo concreto, y registra cada avance.",
        ]
    fresh = [option for option in options if " ".join(option.casefold().split()) not in previous]
    return random.choice(fresh or options)


async def spending_tips(expenses, previous_tips=None):
    previous_tips = previous_tips or []
    totals = defaultdict(lambda: Decimal("0.00"))
    for item in expenses:
        totals[(item.category, item.currency)] += item.amount
    data = sorted(totals.items(), key=lambda pair: pair[1], reverse=True)
    if settings.openai_api_key:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": "Eres un asistente educativo de presupuesto. Da exactamente un consejo breve y nuevo en español. Si hay gastos, basa el consejo en ellos sin mezclar monedas ni inventar datos; si no hay gastos, ofrece un tip práctico para ahorrar. No des asesoría financiera profesional."},
                    {"role": "user", "content": f"Gastos recientes agrupados por categoría y moneda: {data or 'No hay gastos registrados'}. Variante de esta solicitud: {random.randrange(1_000_000)}. Sugiere una recomendación distinta."},
                ],
                max_tokens=120,
                temperature=0.9,
            )
            tip = (response.choices[0].message.content or "").strip()
            normalized_tip = " ".join(tip.casefold().split())
            previous = {" ".join(old.casefold().split()) for old in previous_tips}
            if tip and normalized_tip not in previous:
                return {"tips": tip, "mode": "openai"}
        except Exception:
            # Keep recommendations available if the optional AI service is down.
            pass
    return {"tips": _local_saving_tip(totals, previous_tips), "mode": "reglas locales"}
