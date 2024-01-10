import requests
import yaml
import time
import signal
import sys
from urllib.parse import urlparse

def get_domain(endpoint):
    domain = urlparse(endpoint).netloc
    return domain

def load_config(config_file_path):
    with open(config_file_path, 'r') as file:
        return yaml.safe_load(file)

def health_check(endpoint):
    try:
        response = requests.request(
            method=endpoint.get('method', 'GET'),
            url=endpoint['url'],
            headers=endpoint.get('headers', {}),
            data=endpoint.get('body', None),
            timeout=5
        )

        if 200 <= response.status_code < 300 and response.elapsed.total_seconds() < 0.5:
            return 'UP'
        else:
            return 'DOWN'
    except requests.RequestException:
        return 'DOWN'

def calculate_availability(availbility_metric):
    return round((availbility_metric[0] / availbility_metric[1]) * 100)

def signal_handler(sig, frame):
    print("User pressed CTRL+C. Exiting...")
    sys.exit(0)

def main():
    if len(sys.argv) != 2:
        print("Must give exactly 1 argument - config_file_path.yaml")
        sys.exit(1)

    config_file_path = sys.argv[1]
    endpoints = load_config(config_file_path)

    signal.signal(signal.SIGINT, signal_handler)

    time_count = 0

    try:
        while True:
            results = {}
            print(f"\nTest cycle begins at time = {time_count*15} seconds:")
            
            for endpoint in endpoints:
                status = health_check(endpoint)
                domain = get_domain(endpoint['url'])

                if domain not in results:
                    results[domain] = [0, 0] # key: domain, value: list of (index 0: count of up), (index 1: total count) 
                results[domain][1] += 1            
                if status == 'UP':
                    results[domain][0] += 1  
                # print(f" - Endpoint with name {endpoint['name']} has status {status}")   
                       
            for domain, availbility_metric in results.items():
                print(f"{domain} has {calculate_availability(availbility_metric)}% availability percentage")

            time.sleep(15)
            time_count+=1
    except KeyboardInterrupt:
        print("User pressed CTRL+C. Exiting...")

if __name__ == "__main__":
    main()
