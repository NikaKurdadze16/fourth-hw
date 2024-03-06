import concurrent.futures
import requests
import json
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Manager

urls = []

for i in range(100):
    urls.append(f'https://dummyjson.com/products/{i + 1}')


def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return {url: response.text}  
    except Exception as exc:
        print(f"Error fetching data from {url}: {exc}")
        return {url: None}


def process_urls_chunk(chunk, results_list):
    result_dict = {}
    with ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(fetch_data, url): url for url in chunk}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result_dict.update(future.result())
            except Exception as e:
                print(f"Error processing data from {url}: {e}")
    results_list.append(result_dict)


def main():
    manager = Manager()
    results_list = manager.list()

    chunk_size = 20
    chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]

    with ProcessPoolExecutor(max_workers=5) as process_executor:
        futures = []
        for chunk in chunks:
            future = process_executor.submit(process_urls_chunk, chunk, results_list)
            futures.append(future)

        concurrent.futures.wait(futures)

    with open('data2.json', 'w') as json_file:
        final_results = {}
        for result_dict in results_list:
            final_results.update(result_dict)
        json.dump(final_results, json_file, indent=2)


if __name__ == "__main__":
    main()
