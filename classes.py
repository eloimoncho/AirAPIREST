from datetime import datetime as dt
import mongoengine
from mongoengine.fields import ReferenceField
from pydantic import BaseModel
from typing import List, Optional, Union, Any, Dict

class Waypoint(mongoengine.EmbeddedDocument):
    lat = mongoengine.FloatField(required=True)
    lon = mongoengine.FloatField(required=True)
    height = mongoengine.FloatField(required=True)
    videoStart = mongoengine.BooleanField(required=False)
    videoStop = mongoengine.BooleanField(required=False)

class VideoPlan(mongoengine.EmbeddedDocument):
    mode = mongoengine.StringField(required=True)#static or moving
    #for moving
    latStart = mongoengine.FloatField()
    lonStart = mongoengine.FloatField()
    latEnd = mongoengine.FloatField()
    lonEnd = mongoengine.FloatField()
    #for static
    lat = mongoengine.FloatField()
    lon = mongoengine.FloatField()
    length = mongoengine.IntField()


class Picture(mongoengine.Document):
    path = mongoengine.StringField(required=True)
    lat = mongoengine.FloatField(required=True)
    lon = mongoengine.FloatField(required=True)
    time = mongoengine.DateTimeField(required=True)

    meta = {'collection': 'pictures'}

class Video(mongoengine.Document):
    path = mongoengine.StringField(required=True)
    mode = mongoengine.StringField(required=True)

    # For moving
    latStart = mongoengine.FloatField(required=False)
    lonStart = mongoengine.FloatField(required=False)
    timeStart = mongoengine.DateTimeField(required=False)
    latEnd = mongoengine.FloatField(required=False)
    lonEnd = mongoengine.FloatField(required=False)
    timeEnd = mongoengine.DateTimeField(required=False)

    # For static
    lat = mongoengine.FloatField(required=False)
    lon = mongoengine.FloatField(required=False)
    time = mongoengine.DateTimeField(required=False)

    meta = {'collection': 'videos'}

class FlightPlan(mongoengine.Document):
    Title = mongoengine.StringField(required=True)
    NumWaypoints = mongoengine.IntField(required=True)
    FlightWaypoints = mongoengine.EmbeddedDocumentListField(Waypoint)
    NumPics = mongoengine.IntField(required=True)
    PicsWaypoints = mongoengine.EmbeddedDocumentListField(Waypoint)
    NumVids = mongoengine.IntField(required=True)
    VidWaypoints = mongoengine.EmbeddedDocumentListField(VideoPlan)
    PicInterval = mongoengine.IntField(required=False)
    VidTimeStatic = mongoengine.IntField(required=False)
    DateAdded = mongoengine.DateTimeField(default=dt.now)

    meta = {'collection': 'flightPlan'}


class Flights(mongoengine.Document):
    versionDB = mongoengine.FloatField(default=0.1)
    Title = mongoengine.StringField()
    Date = mongoengine.DateTimeField(default=dt.date)
    Description = mongoengine.StringField()
    startTime = mongoengine.DateTimeField(default=dt.now)
    endTime = mongoengine.DateTimeField()
    GeofenceActive = mongoengine.BooleanField(required=True)
    GeofenceLimits = mongoengine.ObjectIdField()
    FlightPlan = ReferenceField(FlightPlan)
    NumPics = mongoengine.IntField(required=True)
    Pictures = mongoengine.ListField(ReferenceField(Picture))
    NumVids = mongoengine.IntField(required=True)
    Videos = mongoengine.ListField(ReferenceField(Video))
    FlightSuccess = mongoengine.BooleanField()

class FlightData(BaseModel):
    GeofenceActive: bool
    Flightplan: str
    NumPics: float
    NumVids: float

class NewWaypoint(BaseModel):
    lat: float
    lon: float
    height: Optional[float] = 10
    takePic: bool
    videoStart: Optional[bool] = False
    videoStop: Optional[bool] = False
    staticVideo: Optional[bool] = False

class FlightPlanData(BaseModel):
    title: str
    waypoints: List[NewWaypoint]
    PicInterval: Optional[int] = 0
    VidInterval: Optional[int] = 0

class NewVideo(BaseModel):
    idFlight: str
    nameVideo: str
    startVideo: float
    endVideo: float
    latStart: float
    lonStart: float
    latEnd: float
    lonEnd: float

class NewPicture(BaseModel):
    idFlight: str
    namePicture: str
    waypoint: float
    latImage: float
    lonImage: float

class SuccessResponse(BaseModel):
    success: bool
    message: str

    class Config:
        schema_extra = {
            "example": {"success": True, "message": "Waypoints Saved"},
        }

class ErrorResponse(BaseModel):
    success: bool
    message: str
    errors: Optional[List[Dict[str, Any]]] = None

    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "message": "Validation error",
                "errors": [{"loc": ["body", "waypoints"], "msg": "value is not a valid list", "type": "type_error.list"}],
            },
        }



class WaypointMQTT(BaseModel):
    lat: float
    lon: float
    takePic: bool