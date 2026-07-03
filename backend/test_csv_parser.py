import sys
from backend.services.csv_parser import parse_admin_student_list_csv

mock_csv_data = """Emp_ID,Employee_,Emp_Status,Emp_Aadhar,Emp_Mail,Emp_DOB,Emp_Desig,Emp_Locat,Emp_Department
CAN_2001,Aarti Baghel,active,123456789012,aarti@gmail.com,2000-01-01,student,Shalu Beauty Parlour,Beauty Care Assistant
CAN_2002,Pooja Sharma,active,987654321098,pooja@gmail.com,2001-02-02,student,Shalu Beauty Parlour,Beauty Care Assistant
"""

def test():
    print("Testing parser with mock CSV data...")
    try:
        students = parse_admin_student_list_csv(mock_csv_data.encode('utf-8'))
        print(f"Parsed {len(students)} students:")
        for s in students:
            print(s)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
