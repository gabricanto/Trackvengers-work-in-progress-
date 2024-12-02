import requests
from base64 import b64encode

API_KEY = "ca_UVpaM2hGYlczWWhBaEZiOWFjRWRHVHVoLnY0RFNsSVk3aloxbW9talNNaGMyRGc9PQ"
BASE_URL = "https://api.chainabuse.com/v0/reports"
auth_header = f"Basic {b64encode(f'{API_KEY}:{API_KEY}'.encode()).decode()}"

def check_wallet_reports(wallet_address):
    headers = {
        "Authorization": auth_header,
        "Content-Type": "application/json"
    }
    params = {"address": wallet_address}
    
    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        reports = response.json()

        if isinstance(reports, list) and reports:
            for report in reports:
                category = report.get('scamCategory', 'N/A')
                reported_date = report.get('createdAt', 'N/A')
                trusted = report.get('trusted', 'N/A')
                addresses = ", ".join(
                    addr.get('address', 'N/A') for addr in report.get('addresses', [])
                )
                
                print(f"Category: {category}")
                print(f"Reported Date: {reported_date}")
                print(f"Trusted Report: {trusted}")
                print(f"Addresses: {addresses}")
                print("-----------")
        else:
            print("No reports found for this address.")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Example usage
wallet_address = "bc1qdfdxsyd06skh8ldv4dsv9mevvl54qc28qsqyms"
check_wallet_reports(wallet_address)
