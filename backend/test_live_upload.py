import requests
import json

base_url = "https://jss-attendance-portal.onrender.com"

mock_csv_data = """Emp_ID,Employee_,Emp_Status,Emp_Aadhar,Emp_Mail,Emp_DOB,Emp_Desig,Emp_Locat,Emp_Department
CAN_2001,Aarti Baghel,active,123456789012,aarti@gmail.com,2000-01-01,student,Shalu Beauty Parlour,Beauty Care Assistant
CAN_2002,Pooja Sharma,active,987654321098,pooja@gmail.com,2001-02-02,student,Shalu Beauty Parlour,Beauty Care Assistant
"""

def test_live():
    # 1. Login as admin
    print("Logging in as admin...")
    login_url = f"{base_url}/auth/login"
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    r = requests.post(login_url, data=login_data)
    if r.status_code != 200:
        print(f"Login failed: {r.status_code} - {r.text}")
        return
        
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Logged in successfully!")
    
    # 2. Find Shalu Choure's user ID
    # Get global stats containing teachers list
    print("Getting teacher ID...")
    r = requests.get(f"{base_url}/reports/global", headers=headers)
    global_data = r.json()
    shalu_id = None
    for t in global_data["teachers"]:
        if "shalu" in t["username"].lower():
            shalu_id = t["id"]
            break
            
    if not shalu_id:
        print("Shalu Choure not found in teachers list!")
        return
        
    print(f"Found Shalu Choure's ID: {shalu_id}")
    
    # 3. Perform test upload
    print("Uploading mock CSV to live server...")
    upload_url = f"{base_url}/sync/teacher-admin-upload"
    
    files = {
        "file": ("test_students.csv", mock_csv_data.encode('utf-8'), "text/csv")
    }
    data = {
        "teacher_id": shalu_id
    }
    
    r = requests.post(upload_url, headers=headers, data=data, files=files)
    print(f"Upload Response Status: {r.status_code}")
    print(f"Upload Response JSON: {r.json()}")

if __name__ == "__main__":
    test_live()
