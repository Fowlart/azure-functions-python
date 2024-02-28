import datetime
import logging
import os
import time

import azure.functions as func
import http.client
import platform
from urllib.parse import urlencode
import random as r

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


# function to send a message to a telegram bot
@app.schedule(schedule="0 */30 * * * *",
              arg_name="myTimer",
              run_on_startup=True,
              use_monitor=False)
def tg_message_sender(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    system_info = platform.uname()

    encoded_system_info = urlencode({"": f"{system_info.system} {system_info.version}"})[1:]

    logging.info(encoded_system_info)

    tg_token = os.environ.get("TG_TOKEN")
    conn = http.client.HTTPSConnection("api.telegram.org")
    payload = ''
    headers = {}
    conn.request("GET",
                 f"/bot5653183525:{tg_token}/sendMessage?chat_id=5265890390&text=" +
                 encoded_system_info,
                 payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))

    logging.info(f'Python timer trigger function ran at ' +
                 f'{(datetime.datetime.now() + datetime.timedelta(minutes=30)).isoformat()}')


# function to toss a coin
@app.route(route="CoinTossFunction")
@app.blob_output(arg_name="outputBlob",
                 path=f"newblob/test{time.ctime()}.txt",
                 connection="MyStorage")
def CoinTossFunction(req: func.HttpRequest, outputBlob: func.Out[str]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    toss_qty = req.params.get('toss_qty')

    if toss_qty is None:
        return func.HttpResponse(body="Please, provie a query parametr for number of tosses!", status_code=400, )
    else:
        try:
            toss_qty = int(toss_qty)
            resp = []
            for x in range(toss_qty):
                resp.append(r.randint(0, 100) % 2 == 0)
                tru_counts = 0
                false_counts = 0
                for toss_result in resp:
                    if toss_result is True:
                        tru_counts = tru_counts + 1
                    else:
                        false_counts = false_counts + 1
            results = f"true_counts: {tru_counts} | false_counts: {false_counts}"
            outputBlob.set(results)
            return func.HttpResponse(body=results, status_code=200)

        except Exception as e:
            print(f"Exception occurred: {e}")
            return func.HttpResponse(body="The query parametr should be numeric!")