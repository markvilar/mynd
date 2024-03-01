""" Dataclasses for images and camera. """

@dataclass
class Geolocation():
    latitude: float
    longitude: float
    height: float

@dataclass
class Orientation():
    roll: float
    pitch: float
    yaw: float

@dataclass
class Camera():
    label: str
    images: Dict[str, Path]
    geolocation: Geolocation
    orientation: Optional[Orientation]

    def has_orientation(self) -> bool:
        """ Returns true if the camera has an orientation. """
        return not self.orientation is None
