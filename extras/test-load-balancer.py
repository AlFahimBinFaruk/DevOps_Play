#!/usr/bin/env python3
import requests
import json
from collections import Counter
import time

def test_load_balancing(url="http://localhost/info", num_requests=100):
    """Test load balancing by making multiple requests and counting responses from different containers"""
    
    print(f"Testing load balancing with {num_requests} requests...")
    print("-" * 50)
    
    container_ids = []
    response_times = []
    
    for i in range(num_requests):
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                container_id = data.get('container_id', 'unknown')
                container_name=data.get('container_name','unknown')
                container_ids.append(container_id)
                response_times.append(response_time)
                print(f"Request {i+1:2d}: Container {container_name} (Response time: {response_time:.3f}s)")
            else:
                print(f"Request {i+1:2d}: Error - Status code {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request {i+1:2d}: Error - {e}")
    
    # Analyze results
    print("\n" + "="*50)
    print("LOAD BALANCING ANALYSIS")
    print("="*50)
    
    if container_ids:
        counter = Counter(container_ids)
        unique_containers = len(counter)
        
        print(f"Total successful requests: {len(container_ids)}")
        print(f"Unique containers serving requests: {unique_containers}")
        print(f"Average response time: {sum(response_times)/len(response_times):.3f}s")
        print("\nRequest distribution:")
        
        for container_id, count in counter.most_common():
            percentage = (count / len(container_ids)) * 100
            print(f"  Container {container_id}: {count} requests ({percentage:.1f}%)")
        
        print(f"\n✅ Load balancing is {'WORKING' if unique_containers > 1 else 'NOT WORKING'}")
        
        if unique_containers == 1:
            print("   Only one container is responding. Check if scaling worked.")
        elif unique_containers > 1:
            print(f"   Traffic is being distributed across {unique_containers} containers!")
            
    else:
        print("❌ No successful responses received. Check your setup.")

if __name__ == "__main__":
    test_load_balancing()