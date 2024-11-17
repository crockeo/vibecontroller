import json
import time
from pathlib import Path

import requests

from schemas import HueLight


class HueClient:
    CACHE_DIR = Path.cwd() / ".cache"

    def __init__(self, hue_address: str) -> None:
        self._hue_address = hue_address
        self._session = requests.Session()

    @property
    def application_key(self) -> str:
        try:
            with (self.CACHE_DIR / "application_key.json").open() as f:
                cached_application_key = json.load(f)
            return cached_application_key["username"]
        except FileNotFoundError:
            pass

        username, client_key = self._get_application_key()
        self.CACHE_DIR.mkdir(exist_ok=True, parents=True)
        with (self.CACHE_DIR / "application_key.json").open("w") as f:
            json.dump({"username": username, "client_key": client_key}, f)
        return username

    def _get_application_key(self) -> tuple[str, str]:
        while True:
            res = self._session.post(
                f"http://{self._hue_address}/api",
                json={
                    "devicetype": "app_name#instance_name",
                    "generateclientkey": True,
                },
            )
            res.raise_for_status()
            body = res.json()[0]
            if body.get("error", {}).get("type") == 101:
                print("Waiting for link button to be pressed...")
                time.sleep(1.0)
                continue

            username = body.get("success", {}).get("username")
            client_key = body.get("success", {}).get("clientkey")

            if username is None or client_key is None:
                raise ValueError(
                    "hue bridge returned unexecpted value. "
                    "wanted both username and client_key, "
                    f"got {username} and {client_key}"
                )

            return username, client_key

    def list_lights(self) -> dict[str, HueLight]:
        res = self._session.get(
            f"http://{self._hue_address}/api/{self.application_key}/lights",
        )
        res.raise_for_status()
        lights = {}
        for key, value in res.json().items():
            lights[key] = HueLight.model_validate(value)
        return lights

    def put_light(self, light_id: str, light_config: dict) -> None:
        res = self._session.put(
            f"http://{self._hue_address}/api/{self.application_key}/lights/{light_id}/state",
            json=light_config,
        )
        res.raise_for_status()


client = HueClient("10.0.0.200")
# print(client.application_key)

lights = client.list_lights()
for light in lights.values():
    print(light.state)

light_ids = list(client.list_lights().keys())
brightness = 254
while True:
    print(brightness)
    for light_id in light_ids:
        client.put_light(light_id, {"bri": brightness, "transitiontime": 1})
    time.sleep(0.01)
    brightness += 1
    if brightness >= 255:
        brightness = 1
