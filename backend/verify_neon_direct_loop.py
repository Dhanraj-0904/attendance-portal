import requests
import time

base_url = "https://jss-attendance-portal.onrender.com"

def verify_loop():
    print("Polling live login API (direct connection)...")
    for i in range(1, 13):
        print(f"\n[Attempt {i}/12] Waiting 10 seconds...")
        time.sleep(10)
        try:
            login_url = f"{base_url}/auth/login"
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            r = requests.post(login_url, data=login_data, timeout=10)
            print(f"Status Code: {r.status_code}")
            if r.status_code == 200:
                print("SUCCESS: Connection to direct Neon database is fully active and working!")
                print(f"Response: {r.json()}")
                break
            else:
                print(f"Response: {r.text[:200]}")
        except Exception as e:
            print(f"Connection error: {e}")

if __name__ == "__main__":
    verify_loop()
