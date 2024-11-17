from pydantic import BaseModel
from typing import Optional, List


class State(BaseModel):
    on: bool
    bri: int
    ct: int
    alert: str
    colormode: str
    mode: str
    reachable: bool
    hue: Optional[int] = None
    sat: Optional[int] = None
    effect: Optional[str] = None
    xy: Optional[List[float]] = None


class SwUpdate(BaseModel):
    state: str
    lastinstall: str


class ColorGamut(BaseModel):
    min: int
    max: int


class Control(BaseModel):
    mindimlevel: int
    maxlumen: int
    ct: ColorGamut
    colorgamuttype: Optional[str] = None
    colorgamut: Optional[List[List[float]]] = None


class Streaming(BaseModel):
    renderer: bool
    proxy: bool


class Capabilities(BaseModel):
    certified: bool
    control: Control
    streaming: Streaming


class Startup(BaseModel):
    mode: str
    configured: bool


class Config(BaseModel):
    archetype: str
    function: str
    direction: str
    startup: Startup


class HueLight(BaseModel):
    state: State
    swupdate: SwUpdate
    type: str
    name: str
    modelid: str
    manufacturername: str
    productname: str
    capabilities: Capabilities
    config: Config
    uniqueid: str
    swversion: str
    swconfigid: str
    productid: str
