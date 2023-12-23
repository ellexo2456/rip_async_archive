from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

import time
import random
import requests

from concurrent import futures

CALLBACK_URL = "http://localhost:8080/expedition/archieved"
AUTH_KEY = "auth"
executor = futures.ThreadPoolExecutor(max_workers=1)


def get_random_status(video_id):
    time.sleep(5)
    return {
        "id": video_id,
        "status": bool(random.getrandbits(1)),
    }


def status_callback(task):
    try:
        result = task.result()
        print(result)
    except futures._base.CancelledError:
        return

    url = str(CALLBACK_URL + str(result["id"]))
    response = {"archived": result["status"]}
    requests.put(url, data=response, timeout=3)


@api_view(['POST'])
def archived(request):
    if "auth_key" not in request.query_params:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if request.data["auth_key"] != AUTH_KEY:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    if "video_id" in request.data.keys():
        id = request.data["video_id"]

        task = executor.submit(get_random_status, id)
        task.add_done_callback(status_callback)
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(status=status.HTTP_400_BAD_REQUEST)