import httpx

class ExternalDataAgent:
    async def get_fx(self, base: str = "USD"):
        url = f"https://open.er-api.com/v6/latest/{base}"
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                r = await client.get(url)
                r.raise_for_status()
                data = r.json()
                return {"base": base, "rates": data.get("rates", {}), "source": "er-api"}
        except Exception:
            # offline fallback
            return {"base": base, "rates": {"EUR": 0.9, "COP": 4000, "CLP": 900}, "source": "fallback"}
