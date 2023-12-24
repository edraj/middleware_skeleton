import os
from typing import Annotated
from fastapi import Query,Depends
from fastapi.routing import APIRouter 
from api.delivery.requests.create_delivery_request import CreateDeliveryRequest
from api.delivery.requests.update_delivery import UpdateDeliveryRequest
from models.enums import CancellationReasons, DeliverStatus
import requests
import json
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import UploadFile
from pathlib import Path



router = APIRouter()
 

security = HTTPBearer()

@router.post('/create')
async def create_delivery(create_request: CreateDeliveryRequest,credentials: HTTPAuthorizationCredentials= Depends(security)):
    token = credentials.credentials

   
    url = "https://api.oodi.iq/dmart/managed/request"

    payload = json.dumps({
    "space_name": "acme",
    "request_type": "create",
    "records": [
        {
        "resource_type": "ticket",
        "shortname": "auto",
        "subpath": "orders",
        "attributes": {
            "workflow_shortname": "order",
            "is_active": True,
            "payload": {
            "content_type": "json",
            "schema_shortname": "order",
            "body": {
                "mobile_number": create_request.mobile,
                "customer_name": create_request.name,
                "customer_id": "auto",
                "location": {
                "latitude": create_request.location.latitude,
                "longitude": create_request.location.longitude
                },
                "language":create_request.language,
                "iccid": "8858774455555"
            }
            }
        }
        }
    ]
    })
    headers = {
    'Authorization': f'Bearer {token}',
    'Cookie': f'{token}'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

@router.get('/track')
async def track_delivery(shortname: Annotated[str, Query(examples=["b775fdbe"],description='delivery shortname')] ):
       

    url =f"https://api.oodi.iq/dmart/managed/entry/ticket/acme/orders/{shortname}"

    payload = {}
    headers = {
    'Cookie': 'auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7InVzZXJuYW1lIjoiY3VzdG9tZXIifSwiZXhwaXJlcyI6MTcwMzk0MTU4My45MzYzMDA4fQ.2u7h-r-iZuFVtCOnDx65uUJ355_YK2tYhSIz1R7MN7Q; auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7InVzZXJuYW1lIjoiZG1hcnQifSwiZXhwaXJlcyI6MTcwNDIwODYwOC4xMTc5ODcyfQ.jIcaxFCoe439n-FOr7SOiGOvBnHlpRn3MgWLm6XGBuY'
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    return response.json()


@router.put('/cancel')
async def cancel_order(cancellation_reasons:CancellationReasons,shortname:Annotated[str,Query(examples=['b775fdbe'],description='order shortname')],credentials: HTTPAuthorizationCredentials= Depends(security)):
   
    token = credentials.credentials
    url = f"https://api.oodi.iq/dmart/managed/progress-ticket/acme/orders/{shortname}/cancel"
    payload = json.dumps({
    "resolution":cancellation_reasons
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {token}',
    'Cookie': f'{token}'
    }
    print('data payload')
    print(payload)

    response = requests.request("PUT", url, headers=headers, data=payload)
    return response.json()


@router.put('/update')
async def update_delivery(update_delivery: UpdateDeliveryRequest, shortname: Annotated[str, Query(examples=["f7bcb9fe"],description='delivery shortname')],credentials: HTTPAuthorizationCredentials= Depends(security)):
    token=credentials.credentials

    url = "https://api.oodi.iq/dmart/managed/request"

    payload = json.dumps({
    "space_name": "acme",
    "request_type": "update",
    "records": [
        {
        "resource_type": "ticket",
        "shortname": shortname,
        "subpath": "orders",
        "attributes": {
            "state":update_delivery.state,
            "payload": {
            "content_type": "json",
            "schema_shortname": "order",
            "body": {
                            "tracking_id": update_delivery.tracking_id,
                            "planned_delivery_date":update_delivery.planned_delivery_date,
                            "scheduled_delivery":update_delivery.scheduled_delivery,           
                        }
            }
        }
        }
    ]
    })
    headers = {
    'Authorization': f'Bearer {token}',
    'Cookie': f'{token}'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()

   

@router.post('/query')
async def order_query(delivery_status:DeliverStatus):
 

    url = "https://api.oodi.iq/dmart/managed/query"
    payload = json.dumps({
    "type": "search",
    "space_name": "acme",
    "subpath": "/orders",
    "filter_types": [
        "ticket",
        "media"
    ],
    "retrieve_json_payload": True,
    "retrieve_attachments": True,
    "search": f"@state:{delivery_status}",
    "filter_schema_names": [
        "order"
    ]
    })
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    'Cookie': 'auth_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7InVzZXJuYW1lIjoidG90dGVyIn0sImV4cGlyZXMiOjE3MDQyMjUwMTguODA0NjR9.X5HySiP43ii-QZJ3X2T7lBHDt1Wo7MxcA3lrVqaAAXo'
    }
    print(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()

@router.put('/progress',description="needs toter auth ")
async def progress(shortname:Annotated[str,Query(examples=['b775fdbe'],description='order shortname')],credentials: HTTPAuthorizationCredentials= Depends(security)):

    token=credentials.credentials

    url = f"https://api.oodi.iq/dmart/managed/progress-ticket/acme/orders/{shortname}/assign"

    payload = {}
    headers = {
 
    'Cookie': f'auth_token={token}',
    'Authorization': f'Bearer {token}'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

    return response.json()


@router.post('/attachments')
async def upload_attachment(file: UploadFile,
                            shortname:Annotated[str,Query(examples=['b775fdbe'],description='order shortname')],
                            document_name:Annotated[str,Query(examples=['front_citizin_id'],description='document name ')],
                            credentials: HTTPAuthorizationCredentials= Depends(security)):
    # json file path
    token=credentials.credentials
    uploaded_document=await get_file(file)
    uploadAttachmentJson=await get_upload_attachment_json(document_name,shortname)
    files=[
  ('payload_file',('App Store Badge US Black.png',open(uploaded_document,'rb'),'image/png')),
  ('request_record',('uploadAttachmentJson.json',open(uploadAttachmentJson,'rb'),'application/json'))
  ]

    url = "https://api.oodi.iq/dmart/managed/resource_with_payload"
    payload = {'space_name': 'acme'}
    headers = {
    'Cookie': f'auth_token={token}',
    'Authorization': f'Bearer {token}'
    }
    response = requests.request("POST", url, headers=headers, data=payload, files=files)
    os.remove(uploaded_document)
    os.remove(uploadAttachmentJson)
    return response.json()




async def get_upload_attachment_json(document_name,shortname)->str:
    upload_dir=Path()
    uploadAttachmentJson_path = "uploadAttachmentJson.json"
    json_data={
    "attributes": {
    "is_active": True
    },
    "resource_type": "media",
    "shortname": document_name,
    "subpath": f"orders/{shortname}"
    }
    temp_uploadAttachmentJson_dir=upload_dir/uploadAttachmentJson_path
    # Serialize the JSON data and write it to the file
    with open(temp_uploadAttachmentJson_dir, 'w') as json_file:
        json.dump(json_data, json_file)
    return temp_uploadAttachmentJson_dir

async def get_file(file)->str:
    upload_dir=Path()
    data=await file.read()
    temp_save=upload_dir/file.filename
    with open(temp_save,'wb') as f:
        f.write(data)
    return temp_save
