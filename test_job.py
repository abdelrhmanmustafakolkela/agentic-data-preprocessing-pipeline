import requests
import time

job_id = 'a33b66c7-2ac7-4ded-8798-5b2373e86e44'

for i in range(30):
    response = requests.get(f'http://localhost:8000/api/jobs/{job_id}')
    job = response.json()
    print(f'Status: {job["status"]}')
    if job['status'] in ['done', 'failed']:
        print(job)
        break
    time.sleep(2)
