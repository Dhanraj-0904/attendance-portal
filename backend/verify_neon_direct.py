import requests

base_url = "https://jss-attendance-portal.onrender.com"

def verify():
    print("Verifying live login API on the direct connection...")
    try:
        login_url = f"{base_url}/auth/login"
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        r = requests.post(login_url, data=login_data)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {r.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
