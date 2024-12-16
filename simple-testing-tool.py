import requests
import concurrent.futures
import threading
import time
import numpy as np
from datetime import datetime
import sys

def call_api(api_endpoint, request_type, response_times, errors):
      start_time = time.time()
      try:
            if request_type.lower() == 'get':
                  response = requests.get(api_endpoint)
            else:
                  print("Inappropriate HTTP Method")
                  
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            
            if response.status_code != 200:
                  errors.append(1)
            else:
                  errors.append(0)
            
      except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            response_times.append(response_time)
            errors.append(1)
            print(f"API Call Failed : {e} From The Thread {threading.current_thread().name}")
            
def run_iterations(api_endpoint, request_type, iterations, response_times, errors):
      for _ in range(iterations):
            call_api(api_endpoint, request_type, response_times, errors)
            
def calculate_metrics(response_times, errors, total_iterations):
      avg_response_time = np.mean(response_times) if response_times else 0
      p90_response_time = np.percentile(response_times, 90) if response_times else 0
      p99_response_time = np.percentile(response_times, 99) if response_times else 0
      error_percentage = ( sum(errors) / total_iterations ) * 100 if errors else 0
      
      return avg_response_time, p90_response_time, p99_response_time, error_percentage

def generate_html_report(api_endpoint, avg_response_time, p90_response_time, p99_response_time, error_percentage, total_iterations):
      report_html = f"""
                  <html>
                  <head>
                        <title>API Testing Report</title>
                        <style>
                        body {{
                              font-family: Arial, Helvetica, sans-serif;
                              line-height: 1.6;
                              margin: 20px;
                        }}

                        h1 {{
                              text-align: center;
                        }}

                        table {{
                              width: 100%;
                              border-collapse: collapse;
                              margin-top: 20px;
                        }}
                        table, th, td {{
                              border: 1px solid #ddd;
                        }}

                        th, td {{
                              padding: 8px;
                              text-align: left;
                        }}

                        th {{
                              background-color: #f2f2f2;
                        }}
                  </style>
                  </head>

                  <body>
                        <h1>API Test Report</h1>
                        <p>Test date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                        <p><strong>API Endpoint Under Test:</strong> {api_endpoint}</p>
                        <table>
                  <tr>
                        <th>Metric</th>
                        <th>Value</th>
                  </tr>
                  <tr>
                        <td>Number of Iterations</td>
                        <td>{total_iterations}</td>
                  </tr>
                  <tr>
                        <td>Average Response Time (s)</td>
                        <td>{avg_response_time:.4f}</td>
                  </tr>
                  <tr>
                        <td>90th Percentile Response Time (s)</td>
                        <td>{p90_response_time:.4f}</td>
                  </tr>
                  <tr>
                        <td>99th Percentile Response Time (s)</td>
                        <td>{p99_response_time:.4f}</td>
                  </tr>
                  <tr>
                        <td>Error Percentage</td>
                        <td>{error_percentage:.2f}</td>
                  </tr>
            </table>
                  </body>
            </html>
                  """
      with open('api_test_report.html', 'w') as report_file:
            report_file.write(report_html)
      print("HTML Report Generated")
      
def test_api_parallel(numberOfThreads, api_endpoint, request_type, duration, iterations):
      start_time = time.time()
      end_time = start_time + duration
      
      response_times = []
      errors = []
      total_iterations = 0
      
      with concurrent.futures.ThreadPoolExecutor(max_workers=numberOfThreads) as executor:
            while time.time() < end_time:
                  futures = []
                  for _ in range(numberOfThreads):
                        futures.append(executor.submit(run_iterations,api_endpoint, request_type, iterations, response_times, errors))
                  concurrent.futures.wait(futures)
                  total_iterations += numberOfThreads * iterations
                  time.sleep(1)
      avg_response_time, p90_response_time, p99_response_time, error_percentage = calculate_metrics(response_times, errors, total_iterations)
      
      generate_html_report(api_endpoint, avg_response_time, p90_response_time, p99_response_time, error_percentage, total_iterations)
      

if __name__ == '__main__':
      numberOfThreads = int(input('enter number of users / threads : '))
      api_endpoint = input('enter the api endpoint : ')
      request_type = input('enter the request type (e.g. GET) : ')
      duration = int(input('enter the duration for the test (in seconds) : '))
      iterations = int(input('enter the number of iterations : '))
      
      test_api_parallel(numberOfThreads, api_endpoint, request_type, duration, iterations)
