from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

import time
import random
import requests

from concurrent import futures

CALLBACK_URL = "http://localhost:8080/expedition/archived/"
AUTH_KEY = "auth"
executor = futures.ThreadPoolExecutor(max_workers=1)

def get_random_status(videoID):
    time.sleep(5)
    return {
        "id": videoID,
        "status": bool(random.getrandbits(1)),
    }


def status_callback(task):
    try:
        result = task.result()
        print(result)
    except futures._base.CancelledError:
        return

    url = str(CALLBACK_URL + str(result["id"]))
    response = {"archived": result["status"], "authKey": AUTH_KEY}
    response = JsonResponse(response)
    requests.put(url, data=response, timeout=3)



@api_view(['POST'])
def archived(request):
    # if "auth_key" not in request.query_params:
    #     return Response(status=status.HTTP_400_BAD_REQUEST)
    #
    # if request.data["auth_key"] != AUTH_KEY:
    #     return Response(status=status.HTTP_401_UNAUTHORIZED)

    if "videoID" in request.data.keys():
        id = request.data["videoID"]

        task = executor.submit(get_random_status, id)
        task.add_done_callback(status_callback)
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)
