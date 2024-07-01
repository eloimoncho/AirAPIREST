from mongoengine import connect
from classes import *
import json
import os
import asyncio
#from PIL import Image
#from io import BytesIO
#from moviepy.editor import VideoFileClip
#import numpy as np
import datetime
#import cv2 as cv


from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse, StreamingResponse
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
import paho.mqtt.client as mqtt
from pymongo import MongoClient
from bson import ObjectId

myPCip = "localhost"
airHost = "192.168.208.5"
app = FastAPI()
connect(db="DEE", host= "localhost", port=27017)


'''
Esta parte del codigo es para uso del la aplicación movil en flutter.
Aun no sabemos cómo hacer que flutter se connecte con  MQTT. Como alternativa temporal, 
hacemos que flutter se comunique con el autopilot service a través de la APIREST, que si que 
puede comunicarse via MQTT.
En el momento en que se solucione el problema de la conexión de flutter a MQTT esta parte del código
se elmimiará'''

################################################################33

client = mqtt.Client(client_id="fastApi", transport='websockets')
is_connected = False


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {str(rc)}")
    client.subscribe("autopilotService/WebApp/telemetryInfo", 2)
    # client.subscribe("+/fastApi/#", 2)


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global is_connected
    # print(f"{msg.topic} {str(msg.payload)}")
    if msg.topic == "autopilotService/WebApp/telemetryInfo":
        is_connected = True


# MQTT Callbacks
client.on_connect = on_connect
client.on_message = on_message

@app.get("/connection_status")
async def get_connection_status():
    global is_connected
    return {"is_connected": is_connected}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(
            ErrorResponse(
                success=False,
                message="Validation error",
                errors=exc.errors(),
            )
        ),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            ErrorResponse(success=False, message=exc.detail)
        ),
    )

@app.get("/")
def home():
    return RedirectResponse(url="/docs")

@app.post("/add_flightplan", responses={422: {"model": ErrorResponse}})
def add_flightplan(data: FlightPlanData):
    try:
        title = data.title
        waypoints = data.waypoints
        pic_interval = data.PicInterval
        vid_interval = data.VidInterval

        num_waypoints = len(waypoints)
        num_pics = 0
        num_vids = 0
        flight_waypoints = []
        pics_waypoints = []
        vid_waypoints = []
        for w in waypoints:
            waypoint = Waypoint(lat=w.lat, lon=w.lon, height=w.height)
            flight_waypoints.append(waypoint)
            if w.takePic:
                pics_waypoints.append(waypoint)
                num_pics += 1
            if w.videoStart or w.videoStop:
                if w.videoStart:
                    num_vids += 1
                    waypoint_vid = VideoPlan(mode="moving", latStart=w.lat, lonStart=w.lon)
                if w.videoStop:
                    waypoint_vid.latEnd = w.lat
                    waypoint_vid.lonEnd = w.lon
                    vid_waypoints.append(waypoint_vid)
            if w.staticVideo:
                num_vids += 1
                static_vid = VideoPlan(mode="static", lat=w.lat, lon=w.lon, length=vid_interval)
                vid_waypoints.append(static_vid)

        new_flight_plan = FlightPlan(Title=title,
                                     NumWaypoints=num_waypoints,
                                     FlightWaypoints=flight_waypoints,
                                     NumPics=num_pics,
                                     PicsWaypoints=pics_waypoints,
                                     NumVids=num_vids,
                                     VidWaypoints=vid_waypoints,
                                     PicInterval=pic_interval,
                                     VidTimeStatic=vid_interval)
        new_flight_plan.save()
        id_flightplan = str(new_flight_plan.id)
        return {"success": True, "message": "Waypoints Saved", "id": id_flightplan}

    except Exception as e:
        raise HTTPException(status_code=400, detail={str(e)})


@app.post("/add_flight", responses={422: {"model": ErrorResponse}})
def add_flight(data: FlightData):
    try:
        geofence = data.GeofenceActive
        flightplan = ObjectId(data.Flightplan)
        pics = data.NumPics
        vids = data.NumVids

        new_flight = Flights(Date=datetime.date.today(),
                            GeofenceActive=geofence,
                            FlightPlan=flightplan,
                            NumVids=vids,
                            NumPics=pics)
        new_flight.save()
        id_flight = str(new_flight.id)
        return {"success": True, "message": "Waypoints Saved", "id": id_flight}

    except Exception as e:
        raise HTTPException(status_code=400, detail={str(e)})

@app.get("/get_flightplan_id/{flight_id}")
def get_flightplan_id(flight_id: str):
    try:
        client = MongoClient(myPCip+':27017')
        db = client['DEE']
        collection = db['flights']

        flight = collection.find_one({"_id": ObjectId(flight_id)})
        flightplan_id = str(flight["FlightPlan"])
        return ({"FlightPlan id": flightplan_id})
    except Exception as e:
        raise HTTPException(status_code=400, detail={str(e)})


@app.get("/get_flight_plan/{flightplan_title}")
def get_flight_plan(flightplan_title: str):
    try:
        client = MongoClient(myPCip+':27017')
        db = client['DEE']
        collection = db['flightPlan']

        flightplan = collection.find_one({"Title": flightplan_title})
        if flightplan is None:
            return JSONResponse(content=flightplan, status_code=404)
        else:
            flightplan["_id"] = str(flightplan["_id"])
            flightplan["DateAdded"] = flightplan["DateAdded"].isoformat()
            client.close()
            return JSONResponse(content=flightplan, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail={str(e)})

@app.get("/get_flight/{flight_id}")
def get_flight(flight_id: str):
    try:
        client = MongoClient(myPCip+':27017')
        db = client['DEE']
        collection = db['flights']

        flight = collection.find_one({"_id": ObjectId(flight_id)})

        flight["_id"] = str(flight["_id"])
        flight["Date"] = flight["Date"].isoformat()
        flight["startTime"] = flight["startTime"].isoformat()
        flight["FlightPlan"] = str(flight["FlightPlan"])
        client.close()
        return JSONResponse(content=flight, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail={str(e)})

@app.get("/get_pic_interval/{flightplan_id}")
def get_pic_interval(flightplan_id: str):
    try:
        client = MongoClient(myPCip+':27017')
        db = client['DEE']
        collection = db['flightPlan']

        flightplan = collection.find_one({"_id": ObjectId(flightplan_id)})
        pic_Interval = flightplan["PicInterval"]
        return {"Pic interval": pic_Interval}
    except Exception as e:
        raise HTTPException(status_code=400, detail={str(e)})

@app.get("/get_vid_interval/{flightplan_id}")
def get_vid_interval(flightplan_id: str):
    try:
        client = MongoClient(myPCip+':27017')
        db = client['DEE']
        collection = db['flightPlan']

        flightplan = collection.find_one({"_id": ObjectId(flightplan_id)})
        vid_Interval = flightplan["VidTimeStatic"]
        return {"Vid interval": vid_Interval}
    except Exception as e:
        raise HTTPException(status_code=400, detail={str(e)})

@app.put("/add_video", response_model=SuccessResponse, responses={422: {"model": ErrorResponse}})
async def add_video(data: NewVideo):
    try:
        client = MongoClient(myPCip+':27017')
        db = client['DEE']
        collection = db['flights']

        flight_id = data.idFlight
        name_video = data.nameVideo
        startVideo = data.startVideo
        endVideo = data.endVideo
        latStartVideo = data.latStart
        lonStartVideo = data.lonStart
        latEndVideo = data.latEnd
        lonEndVideo = data.lonEnd

        flightplan = collection.find_one({"_id": ObjectId(flight_id)})

        if flightplan:
            flightplan["Videos"].append({
                "startWaypoint": startVideo,
                "endWaypoint": endVideo,
                "nameVideo": name_video,
                "latStart": latStartVideo,
                "lonStart": lonStartVideo,
                "latEnd": latEndVideo,
                "lonEnd": lonEndVideo})
            collection.replace_one({"_id": ObjectId(flightplan["_id"])}, flightplan)
            return {"success": True, "message": "Video saved"}
    except Exception as e:
        raise HTTPException(status_code=400, detail={str(e)})

@app.put("/add_picture", response_model=SuccessResponse, responses={422: {"model": ErrorResponse}})
async def add_picture(data: NewPicture):
    try:

        client = MongoClient(myPCip+':27017')
        db = client['DEE']
        collection = db['flights']

        flight_id = data.idFlight
        name_picture = data.namePicture
        lat_image = data.latImage
        lon_image = data.lonImage

        flightplan = collection.find_one({"_id": ObjectId(flight_id)})

        if flightplan:
            flightplan["Pictures"].append({
                "waypoint": data.waypoint,
                "namePicture": name_picture,
                "lat": lat_image,
                "lon": lon_image})
            collection.replace_one({"_id": ObjectId(flightplan["_id"])}, flightplan)
            return {"success": True, "message": "Picture saved"}
    except Exception as e:
        raise HTTPException(status_code=400, detail={str(e)})

@app.get("/get_results_flight/{flight_id}")
def get_results_flight(flight_id: str):
    try:
        client = MongoClient(myPCip+':27017')
        db = client['DEE']
        collection = db['flights']

        flight = collection.find_one({"_id": ObjectId(flight_id)})
        videos = flight["Videos"]
        pictures = flight["Pictures"]
        return ({"Videos": videos, "Pictures": pictures})
    except Exception as e:
        raise HTTPException(status_code=400, detail={str(e)})

@app.get("/get_all_flightPlans")
def get_all_flightPlans():
    waypoints = json.loads(FlightPlan.objects().to_json())
    return {"Waypoints": waypoints}

