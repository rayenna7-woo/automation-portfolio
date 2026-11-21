# import requests
# url="https://httpbin.org/status/500"
# params={"service": "lead-capture", "budget": "200"}
# headers={"X-Client": "demo"}
# response=requests.request("GET",url,params=params,headers=headers,timeout=10)
# if response.status_code==200:
    # response_body=response.json()["args"]
    # print(type(response.json()["args"]["budget"]))
# else:
    # response_body=response.text
# 
# result={
    # "final_url" :response.url,
    # "status_code":response.status_code,
    # "Content type": response.headers["Content-Type"],
    # "body": response_body
# }
# print(result)

from http_anatomy import inspect_request
inspect_request("GET", "https://httpbin.org/delay/5", timeout=2)