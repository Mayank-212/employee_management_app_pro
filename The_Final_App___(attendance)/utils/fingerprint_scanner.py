# utils/fingerprint_scanner.py

def scan_fingerprint(employee_db):
    # Simulated scanner for demo/testing
    print("[SCAN] Place your finger on the scanner...")
    entered_id = input("Enter Employee ID (simulated): ").strip()

    if entered_id in employee_db:
        return entered_id
    else:
        print("❌ Invalid fingerprint / Employee not found.")
        return None
