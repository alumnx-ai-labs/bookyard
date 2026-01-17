
import urllib.request
import urllib.error
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(endpoint, base_url=None):
    url = f"{base_url or BASE_URL}{endpoint}"
    print(f"Testing {url}...", end=" ")
    try:
        with urllib.request.urlopen(url) as response:
            status = response.getcode()
            print(f"Status: {status}")
            data = json.loads(response.read())
            # print(f"Response: {data}")
            return status == 200
    except urllib.error.HTTPError as e:
        print(f"Failed: {e.code} - {e.reason}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False


print("Verifying API V1 Endpoints...")
docs_ok = test_endpoint("/docs", base_url="http://localhost:8000")
books_ok = test_endpoint("/api/v1/books", base_url="http://localhost:8000")

if docs_ok and books_ok:
    print("✓ API is healthy")
elif docs_ok:
    print("✓ Docs reachable but Books failed (Endpoint specific error)")
else:
    print("✗ API is completely down (Global error)")
