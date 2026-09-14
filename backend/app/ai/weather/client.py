"""AI 캐디(Phase 8)용 실시간 날씨 조회.

Open-Meteo(https://open-meteo.com)는 가입/API 키 없이 쓸 수 있는 무료 날씨 API다 —
STT가 로컬 faster-whisper를 쓰는 것과 같은 원칙(과금·키 없이 진짜 외부 데이터를 쓴다)을
날씨에도 적용했다. 좌표는 app/seed_courses.py에 실제 지역 좌표로 미리 채워 넣었다.
"""
import httpx

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# WMO 날씨 코드(Open-Meteo가 그대로 씀) 중 자주 나오는 것만 한국어로 매핑한다.
_WEATHER_CODE_KO = {
    0: "맑음",
    1: "대체로 맑음",
    2: "부분적으로 흐림",
    3: "흐림",
    45: "안개",
    48: "짙은 안개",
    51: "약한 이슬비",
    53: "이슬비",
    55: "강한 이슬비",
    61: "약한 비",
    63: "비",
    65: "강한 비",
    71: "약한 눈",
    73: "눈",
    75: "강한 눈",
    80: "약한 소나기",
    81: "소나기",
    82: "강한 소나기",
    95: "뇌우",
}


class WeatherFetchError(Exception):
    """외부 날씨 API 호출에 실패했을 때."""


def get_current_weather(latitude: float, longitude: float) -> dict:
    try:
        response = httpx.get(
            OPEN_METEO_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,wind_speed_10m,precipitation,weather_code",
                "timezone": "Asia/Seoul",
            },
            timeout=5.0,
        )
        response.raise_for_status()
        current = response.json()["current"]
    except Exception as exc:
        raise WeatherFetchError("날씨 정보를 가져오지 못했습니다.") from exc

    code = current.get("weather_code")
    return {
        "temperature_c": current.get("temperature_2m"),
        "wind_speed_kmh": current.get("wind_speed_10m"),
        "precipitation_mm": current.get("precipitation"),
        "condition": _WEATHER_CODE_KO.get(code, "알 수 없음"),
    }


def format_weather_summary(weather: dict | None) -> str:
    if weather is None:
        return "날씨 정보 없음"
    return (
        f"{weather['condition']}, 기온 {weather['temperature_c']}°C, "
        f"풍속 {weather['wind_speed_kmh']}km/h, 강수량 {weather['precipitation_mm']}mm"
    )
