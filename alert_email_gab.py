import smtplib
import requests
import time

# Configuration
EMAIL_ADDRESS = "trackvengers@gmail.com"  # Your email address (sender)
EMAIL_PASSWORD = "rzbvgnrjmthpmhlz"  # Your app password (or regular password if 2FA is off)
BITCOIN_API = "https://api.blockcypher.com/v1/btc/main/addrs/"
THRESHOLD_AMOUNT = 0.01  # Minimum Bitcoin amount to trigger an alert (in BTC)
CHECK_INTERVAL = 60  # Time interval to check (in seconds)

# Function to send an email alert
def send_email_alert(sender_email, sender_password, recipient_email, subject, message):
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            email_message = f"Subject: {subject}\n\n{message}"
            server.sendmail(sender_email, recipient_email, email_message)
        print(f"Email sent to {recipient_email}: {subject}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Function to monitor a Bitcoin wallet
def monitor_wallet(wallet_address, recipient_email):
    last_tx_hash = None  # Track the last transaction hash

    while True:
        try:
            # Fetch wallet data using Blockcypher API
            response = requests.get(f"{BITCOIN_API}{wallet_address}/full")
            print("API Response:", response.text)  # Debugging line to print raw response
            response.raise_for_status()  # Ensure no 404/500 errors
            data = response.json()
            if not data:
                print("No data returned from the API.")
                continue  # Skip to the next iteration
            
            transactions = data["txs"]
            
            # Check the latest transaction
            if transactions:
                latest_tx = transactions[0]
                tx_hash = latest_tx["hash"]
                
                # Sum the output values (converted to BTC)
                value = sum(output["value"] for output in latest_tx["outputs"]) / 1e8  # Convert Satoshi to BTC
                fees = latest_tx["fees"] / 1e8  # Convert Satoshi to BTC
                
                print(f"Transaction Hash: {tx_hash}, Value: {value} BTC, Fees: {fees} BTC")
                
                # Only proceed if this is a new transaction and meets the threshold
                if tx_hash != last_tx_hash:
                    last_tx_hash = tx_hash
                    
                    # Filter based on criteria
                    if value >= THRESHOLD_AMOUNT and fees < value:
                        subject = "🚨 Bitcoin Transaction Alert"
                        message = (
                            f"A significant Bitcoin transaction was detected!\n\n"
                            f"Wallet Address: {wallet_address}\n"
                            f"Transaction Hash: {tx_hash}\n"
                            f"Amount: {value:.8f} BTC\n"
                            f"Fee: {fees:.8f} BTC"
                        )
                        send_email_alert(EMAIL_ADDRESS, EMAIL_PASSWORD, recipient_email, subject, message)
        except requests.exceptions.RequestException as e:
            print(f"Error with API request: {e}")
            time.sleep(CHECK_INTERVAL)  # Wait before retrying
            continue
        except ValueError as e:
            print(f"Error parsing JSON: {e}")
            time.sleep(CHECK_INTERVAL)
            continue
        
        # Wait before checking again
        time.sleep(CHECK_INTERVAL)

# Main Function
if __name__ == "__main__":
    wallet_address = input("Enter the Bitcoin wallet address to monitor: ")
    recipient_email = input("Enter the recipient email for alerts: ")
    print(f"Monitoring wallet {wallet_address} for large transactions...")
    monitor_wallet(wallet_address, recipient_email)
