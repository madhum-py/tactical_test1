import requests
import sys
import os
import logging
from datetime import datetime
import time

token = sys.argv[1]
triggered_by_common = sys.argv[2]

current_timestamp_raw = datetime.now()
current_timestamp = current_timestamp_raw.strftime("%Y%m%d-%I%M%S")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

gh_access_token = f'token {token}'

headers = {
    'Authorization': gh_access_token
}

proceed = False


logging.info("Checking if there are any Jobs in Queue or In Progress")
no_wait = True
while True:
    response = requests.request(method="GET", url="https://api.github.com/repos/madhum-py/common_test/actions/runs?per_page=30", headers = headers)
    if 'Link' in response.headers.keys():
        link_header = (response.headers)['Link'].split(";")
        last_index = link_header.index(' rel="last"')
        number_of_pages = int(link_header[last_index - 1].split("page")[-1].strip("=").strip(">"))
        #print(number_of_pages)
    count = 1
    go_ahead = True
    for i in response.json()['workflow_runs']:
        #if count == 1:
        #    first_job_name = i['name']
        #    count += 1
        #    continue
        #print(f"--- {count} ---")
        count += 1
        workflow_name = i['name']
        workflow_started_at = i['created_at']
        workflow_status = i['status']
        workflow_run_number = i['run_number']

        status_list = ["in_progress", "queued", "requested", "waiting"]
        if workflow_status in status_list:
            logging.info(f"Workflow '{workflow_name} (Run Number : #{workflow_run_number}) is currently in '{workflow_status}' State.")
            logging.info(f"Triggered by Common: {triggered_by_common}")
            if triggered_by_common == "true":
                logging.info("This Job has been triggered by Upstream Workflow. Hence, moving to next steps")
                break
                #sys.exit(1)
                
            #os.system("sleep 5")
            else:
                logging.info("Hence, stopping the workflow")
                sys.exit(1)
            go_ahead = False
            no_wait = False
            break

        if count == 12:
            break

    if go_ahead: 
        if triggered_by_common != "true":
            logging.info("Common job is not in Queued/In Progress state. Hence, starting the Workflow")
        break