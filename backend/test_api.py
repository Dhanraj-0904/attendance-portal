import urllib.request
import urllib.parse
import json

def test_endpoints():
    url = "http://127.0.0.1:8000"
    
    # 1. Login
    print("Testing Login...")
    payload = urllib.parse.urlencode({
        "username": "admin",
        "password": "admin123"
    }).encode("utf-8")
    
    req = urllib.request.Request(f"{url}/auth/login", data=payload, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    try:
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode())
            token = data["access_token"]
            print("Login successful. Token acquired.")
    except Exception as e:
        print("Login failed:", e)
        if hasattr(e, "read"):
            print(e.read().decode())
        return

    # 2. Get Global Stats
    print("\nTesting /reports/global...")
    req2 = urllib.request.Request(f"{url}/reports/global", method="GET")
    req2.add_header("Authorization", f"Bearer {token}")
    
    try:
        with urllib.request.urlopen(req2) as res2:
            data2 = json.loads(res2.read().decode())
            print("Status code: 200")
            print("Global reports response keys:", list(data2.keys()))
    except Exception as e:
        print("Global reports failed:", e)
        if hasattr(e, "read"):
            print(e.read().decode())

    # 3. Get Batches
    print("\nTesting /batches/...")
    req3 = urllib.request.Request(f"{url}/batches/", method="GET")
    req3.add_header("Authorization", f"Bearer {token}")
    
    try:
        with urllib.request.urlopen(req3) as res3:
            data3 = json.loads(res3.read().decode())
            print("Status code: 200")
            print("Batches response size:", len(data3))
    except Exception as e:
        print("Batches failed:", e)
        if hasattr(e, "read"):
            print(e.read().decode())

if __name__ == "__main__":
    test_endpoints()
