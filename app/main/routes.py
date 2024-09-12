import datetime

import requests
from app.main import router
from fastapi import Request
from pydantic import BaseModel
from pydash import objects


class ClosingTime(BaseModel):
    close: str


class OpeningTimes(ClosingTime):
    open: str


class OpeningTimesDay(OpeningTimes):
    day: str
    day_alt: str

    def __init__(self, open: str, close: str, day_number: int):
        days = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        today_dow = (datetime.datetime.today().weekday() + 1) % 7
        day_alt = ""
        if today_dow == day_number:
            day_alt = "today"
        elif (today_dow + 1) % 7 == day_number:
            day_alt = "tomorrow"
        super().__init__(
            open=open, close=close, day=days[day_number], day_alt=day_alt
        )


@router.get("/is-open-now/")
async def is_open_now(
    request: Request,
) -> bool:
    config = request.app.state.config
    url = f"https://maps.googleapis.com/maps/api/place/details/json?fields=current_opening_hours%2Copening_hours%2Csecondary_opening_hours&place_id={config['GOOGLE_MAPS_PLACE_ID']}&key={config['GOOGLE_MAPS_API_KEY']}"
    response = requests.get(url)
    if response.status_code == 404:
        raise Exception("Resource not found")
    if response.status_code != requests.codes.ok:
        raise ConnectionError("Request to API failed")
    try:
        result = response.json()
    except ValueError:
        raise ConnectionError("Cannot parse JSON")
    return objects.get(result, "result.current_opening_hours.open_now") or False


@router.get("/today/")
async def today(
    request: Request,
) -> OpeningTimes:
    config = request.app.state.config
    url = f"https://maps.googleapis.com/maps/api/place/details/json?fields=current_opening_hours%2Copening_hours%2Csecondary_opening_hours&place_id={config['GOOGLE_MAPS_PLACE_ID']}&key={config['GOOGLE_MAPS_API_KEY']}"
    response = requests.get(url)
    if response.status_code == 404:
        raise Exception("Resource not found")
    if response.status_code != requests.codes.ok:
        raise ConnectionError("Request to API failed")
    try:
        result = response.json()
    except ValueError:
        raise ConnectionError("Cannot parse JSON")
    today_dow = (datetime.datetime.today().weekday() + 1) % 7
    if current_opening_hours := objects.get(
        result, "result.current_opening_hours"
    ):
        if periods := objects.get(current_opening_hours, "periods"):
            today_opening_times = (
                next(
                    period
                    for period in periods
                    if period["open"]["day"] == today_dow
                )
                or periods[0]
            )
            return OpeningTimes(
                open=today_opening_times["open"]["time"],
                close=today_opening_times["close"]["time"],
            )
    raise ConnectionError("Cannot parse data")


@router.get("/next-open/")
async def next_open(
    request: Request,
) -> OpeningTimesDay:
    config = request.app.state.config
    url = f"https://maps.googleapis.com/maps/api/place/details/json?fields=current_opening_hours%2Copening_hours%2Csecondary_opening_hours&place_id={config['GOOGLE_MAPS_PLACE_ID']}&key={config['GOOGLE_MAPS_API_KEY']}"
    response = requests.get(url)
    if response.status_code == 404:
        raise Exception("Resource not found")
    if response.status_code != requests.codes.ok:
        raise ConnectionError("Request to API failed")
    try:
        result = response.json()
    except ValueError:
        raise ConnectionError("Cannot parse JSON")
    print(result)
    if current_opening_hours := objects.get(
        result, "result.current_opening_hours"
    ):
        if periods := objects.get(current_opening_hours, "periods"):
            today_dow = (datetime.datetime.today().weekday() + 1) % 7
            now = datetime.datetime.now().strftime("%H%M")
            next_opening_times = (
                next(
                    period
                    for period in periods
                    if period["open"]["day"] > today_dow
                    or (
                        period["open"]["day"] == today_dow
                        and int(period["open"]["time"]) > int(now)
                    )
                )
                or periods[0]
            )
            return OpeningTimesDay(
                open=next_opening_times["open"]["time"],
                close=next_opening_times["close"]["time"],
                day_number=next_opening_times["open"]["day"],
            )
    raise ConnectionError("Cannot parse data")
