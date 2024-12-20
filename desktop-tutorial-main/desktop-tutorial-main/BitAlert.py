import matplotlib
matplotlib.use('Agg')  # Configura Matplotlib per il backend "Agg"
from flask import Flask, request, render_template, send_file
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import re


app = Flask(__name__)     # Inizializza l'app Flask


# Configurazione email
EMAIL_ADDRESS = "trackvengers@gmail.com"  # Email del mittente
EMAIL_PASSWORD = "rzbvgnrjmthpmhlz"  # App password generata


# Lista di wallet conosciuti
KNOWN_WALLETS = {
    "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa": "Satoshi Nakamoto (Genesis Block)",
    "1P5ZEDWTKTFGxQjZphgWPQUpe554WKDfHQ": "Binance Hot Wallet",
}

# Cluster noti (exchange, ransomware, mixer, ecc.)
CLUSTERS = {
    "Exchange": {
        "3Qa13xfjS9vT9iEKChKqbgMzrh9LUUuA2V":  "Binance",
        "3FgkTfWLiVqRbpMGwNn6zR4UZ69PdPgNwK":  "Coinbase",
        "3EKy8Ecp9u4XPkAvkdsSzJ86SVJNtPdtkR":  "Kraken",
        "3BtFnX5t3KQRW4YkE92pAmf7uZTk2XtWVq":  "Bitfinex",
        "3GeMiNi9Xy78T5RKL8WYmZTqJn6AkJWV7Q":  "Gemini",
        "3HuOBi9Ty74XKLmY5aRQPz9WN8Tm9RKL7F":  "Huobi",
        "3KuCoIN9YKL7m5AkJTQzPWL4XmNY9RK7F":   "KuCoin",
        "3BtSTaMp9WRKLN6TY5RQPZ8XTW7MKL4YmN":  "Bitstamp",
        "3OKExN7KQRWYP8MZT5A9LnXTWm6RKJLP7Q":  "OKEx",
        "3BTRexY8MNL5Tk6RQPZYWXT7MKJLP4A9F":   "Bittrex"
    },
    "Ransomware": {
        "1HB5XMLmzFVj8ALj6mfBsbifRoD4miY36v":  "WannaCry",
        "1DiRNZnRFiTEj3nRrvABKYG1PAGSn5Jja9":  "Locky",
        "13AM4VW2dhxYgXeQepoHkHSQuy6NgaEb94":  "CryptoLocker",
        "1Mz7153HMuxXTuR2R1t78mGSdzaAtNbBWX":  "Petya/NotPetya",
        "19JsPo56ErskH5mLe4DYyPSRfbswz4CZtd":  "Cerber",
        "1QAj6zfwRgKY9nuJaZ92pADk55H9EofXMB":  "TeslaCrypt",
        "1LZsAKDZc1uA9A16i2UucdD8rpyDMG85zL":  "REvil/Sodinokibi",
        "1J6PYEzr4CUoGbnXrELyHszoTSz3wCsCaj":  "Conti",
        "1C6g1yj8Tk8AkzNC73f6HPMgmSjFc6Qbo3":  "Ryuk",
        "19QgbLQwUgiow8NgkRAim6pm1E7yobUbMz":  "Maze",
        "3Cbq7aT1tY8kMxWLbitaG7yT6bPbKChq64":  "Egregor",
        "3Ki94CtTdk8K7AeCynJcMTCRxY6KYSs4nR":  "DoppelPaymer",
        "3GWPAaEeehTQycBdw9ULshnF4ZQeJ3WqTx":  "NetWalker",
        "3FxFQ9N3JKq4J66M6mCjKrdsBWEzAGhZPr":  "BitPaymer",
        "12t9YDPgwueZ9NyMgw519p7AA8isjr6SMw":  "SamSam",
        "1PPrZ5sRf1RxyGyWp5f8hXNBG9yKmANkMT":  "Avaddon",
        "1JXonhH9p3zTkjqjRxU44X5xwGg7SJmsQR":  "Clop",
        "3KbZ7m1c2ey98dZPEYHQbFS6AjvMkPXjHg":  "DarkSide",
        "3HgiXNyvCRzvdT7NbXzRQEqU4h8odZr3eV":  "Hive",
        "1BcBXL6cY5hrQBiJDQfMbVkDkqM3L3CXLd":  "BlackMatter"
    },
    "Mixer": {
        "3EDvLXRqUtQR7b9GzGyko38GKtWEKFiJET":  "Helix",
        "3NLF26Yg6gSuUZYMtpJSmUe9dy36E2A3XU":  "ChipMixer",
        "3DpB8NrPMeFvnTNnWKy9zRfdXsxhxFRWUD":  "Tornado Cash",
        "3WaSBiwV6THByk9gKcJ63X43EjRmQtWDCK":  "Wasabi Wallet",
        "3SAMrKrH3TKghJ4FgDr9k7U9AkPC3D7TQD":  "Samourai Wallet",
        "3BLeNdr7A9MyhRuXc7FyT2HR8d6CRPC4EX":  "Blender.io",
        "3FogYTa8LRHT9qZGKyX4J39c4U2bWRFeFQ":  "Bitcoin Fog",
        "3MiXtUMyKoKj9QEd9P7YWzz2RAuD7WRKL2":  "MixTum.io",
        "3PRivCoYn8WRXyKjXtP74D22MPyAKWRK7L":  "PrivCoin",
        "3AlPhABayMiXe9WR8TWYZ34WRKmXt7KXRD":  "AlphaBay Mixer"
    }
}

# Storico delle ricerche
search_history = []

@app.template_filter('timestamp_to_date')
def timestamp_to_date_filter(timestamp):
    """
    Converte un timestamp Unix in una stringa formattata come 'dd-mm-yyyy HH:MM:SS'.
    """
    return datetime.utcfromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M:%S')

def get_wallet_owner(wallet_address):
    return KNOWN_WALLETS.get(wallet_address, "Sconosciuto")

def get_btc_to_eur_rate():
    """
    Recupera il tasso di cambio corrente BTC/EUR utilizzando l'API di CoinGecko.
    """
    api_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        return data["bitcoin"]["eur"]
    except requests.exceptions.RequestException as e:
        print(f"Errore nel recupero del tasso di cambio: {e}")
        return None

def get_current_block_height():
    """
    Recupera l'altezza attuale dell'ultimo blocco conosciuto sulla blockchain.
    """
    api_url = "https://blockchain.info/q/getblockcount"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return int(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Errore nel recupero dell'altezza del blocco: {e}")
        return None

def get_transactions(wallet_address):
    api_url = f"https://blockchain.info/rawaddr/{wallet_address}?limit=50"
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        transactions = sorted(data.get("txs", []), key=lambda tx: tx['time'], reverse=True)
        return transactions
    except requests.exceptions.RequestException as e:
        print(f"Errore nella richiesta: {e}")
        return None  # Restituisci None per indicare un errore

def analyze_wallet_cluster(wallet_address):
    """
    Determina se il wallet appartiene a un cluster noto e restituisce il nome del cluster e il nome specifico.
    """
    for cluster_name, addresses in CLUSTERS.items():
        if wallet_address in addresses:
            specific_name = addresses[wallet_address]
            return f"{cluster_name} - {specific_name}"
    return None

def parse_price_range(price_filter):
    """
    Converte i range di prezzo predefiniti in valori numerici.
    """
    ranges = {
        "0-10": (0, 10),
        "10-50": (10, 50),
        "50-100": (50, 100),
        "100-300": (100, 300),
        "300-500": (300, 500),
        "500-1000": (500, 1000),
        "1000+": (1000, float('inf'))
    }
    return ranges.get(price_filter, (0, float('inf')))

def parse_transaction(tx, wallet_address, btc_to_eur_rate, current_block_height):
    """
    Analizza una singola transazione per estrarre le informazioni necessarie.
    """
    inputs = tx.get("inputs", [])
    outputs = tx.get("out", [])
    is_outgoing = any(inp.get("prev_out", {}).get("addr") == wallet_address for inp in inputs)
    is_incoming = any(out.get("addr") == wallet_address for out in outputs)
    direction = "Uscita" if is_outgoing else "Entrata" if is_incoming else "Sconosciuta"
    total_value_satoshi = sum(out["value"] for out in outputs if out.get("addr") != wallet_address)
    total_value_btc = total_value_satoshi / 100000000
    total_value_eur = total_value_btc * btc_to_eur_rate

    # Calcola le conferme
    block_height = tx.get("block_height")
    if block_height is None:
        confirmations_status = "Pending"
    else:
        confirmations = current_block_height - block_height + 1
        confirmations_status = f"{confirmations} conferme"

    tx_link = f"https://www.blockchain.com/btc/tx/{tx['hash']}"  # Link al blockchain explorer
    return {
        "hash": tx["hash"],
        "time": tx["time"],
        "value_btc": total_value_btc,
        "value_eur": total_value_eur,
        "direction": direction,
        "confirmations": confirmations_status,
        "explorer_link": tx_link
    }

def filter_transactions(transactions, direction=None, start_date=None, end_date=None, price_range=None, status=None):
    """
    Filtra le transazioni in base a direzione (Entrata/Uscita), intervallo di date e range di prezzo.
    """
    filtered = transactions

    if direction:  # Filtro basato sulla direzione
        filtered = [tx for tx in filtered if tx['direction'] == direction]
        
    if price_range:  # Filtro per prezzo (EUR)
        min_price, max_price = parse_price_range(price_range)
        filtered = [
            tx for tx in filtered if min_price <= tx['value_eur'] < max_price
        ]
        
    if status: # Filtro per stato
        if status == "Confermato":
            filtered = [tx for tx in filtered if "conferme" in tx['confirmations']]
        elif status == "Pending":
            filtered = [tx for tx in filtered if tx['confirmations'] == "Pending"]
        elif status == "Non Confermato":
            filtered = [tx for tx in filtered if "non confermato" in tx['confirmations']]

    if start_date:  # Filtro per data di inizio
        start_timestamp = datetime.strptime(start_date, '%Y-%m-%d').timestamp()
        filtered = [tx for tx in filtered if tx['time'] >= start_timestamp]

    if end_date:  # Filtro per data di fine
        end_timestamp = datetime.strptime(end_date, '%Y-%m-%d').timestamp()
        filtered = [tx for tx in filtered if tx['time'] <= end_timestamp]


    return filtered

def generate_combined_flow_graph(wallet_address, transactions):
    """
    Genera un grafico unico per confrontare entrate e uscite.
    """
    dates = []
    inflows = []
    outflows = []

    for tx in transactions:
        date = datetime.utcfromtimestamp(tx['time']).strftime('%d-%m-%Y')
        value_btc = tx['value_btc']

        if tx['direction'] == "Entrata":
            dates.append(date)
            inflows.append(value_btc)
            outflows.append(0)  # Nessuna uscita
        elif tx['direction'] == "Uscita":
            dates.append(date)
            inflows.append(0)  # Nessuna entrata
            outflows.append(value_btc)

    # Ordina i dati in ordine cronologico crescente
    sorted_data = sorted(zip(dates, inflows, outflows), key=lambda x: datetime.strptime(x[0], '%d-%m-%Y'))
    dates, inflows, outflows = zip(*sorted_data) if sorted_data else ([], [], [])

    # Creazione del grafico
    plt.figure(figsize=(10, 6))
    plt.plot(dates, inflows, label="Entrate", color="green", marker="o")
    plt.plot(dates, outflows, label="Uscite", color="red", marker="o")
    plt.xlabel("Data")
    plt.ylabel("Bitcoin (BTC)")
    plt.title(f"Flussi di Bitcoin per: {wallet_address}", fontsize=14, fontweight="bold")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    # Salva il grafico con un nome unico basato sul wallet
    output_path = f"static/{wallet_address}_combined_flow_plot.png"
    plt.savefig(output_path)
    plt.close()  # Chiudi il grafico per evitare conflitti
    return output_path

def generate_separate_flow_graph(wallet_address, transactions, flow_type):
    """
    Genera grafici separati per entrate e uscite.
    """
    dates = []
    values = []

    for tx in transactions:
        date = datetime.utcfromtimestamp(tx['time']).strftime('%d-%m-%Y')
        if tx['direction'] == flow_type:
            dates.append(date)
            values.append(tx['value_btc'])

    # Ordina i dati in ordine cronologico crescente
    sorted_data = sorted(zip(dates, values), key=lambda x: datetime.strptime(x[0], '%d-%m-%Y'))
    dates, values = zip(*sorted_data) if sorted_data else ([], [])

    # Creazione del grafico
    plt.figure(figsize=(10, 6))
    plt.bar(dates, values, color="green" if flow_type == "Entrata" else "red")
    plt.xlabel("Data")
    plt.ylabel("Bitcoin (BTC)")
    plt.title(f"{flow_type} di Bitcoin per: {wallet_address}", fontsize=14, fontweight="bold")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Salva il grafico con un nome unico basato sul wallet
    output_path = f"static/{wallet_address}_{flow_type.lower()}_flow_plot.png"
    plt.savefig(output_path)
    plt.close()  # Chiudi il grafico per evitare conflitti
    return output_path

def send_email(to_email, subject, body):
    """
    Invia un'email al destinatario specificato.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email inviata correttamente a {to_email}")
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {e}")
        
def monitor_wallet(wallet_address, email):
    """
    Monitora il wallet Bitcoin per nuove transazioni confermate e invia un'email all'utente in caso di attività.
    """
    print(f"Iniziando il monitoraggio per il wallet {wallet_address}...")
    start_time = int(datetime.utcnow().timestamp())  # Timestamp iniziale
    known_transactions = set()  # Per memorizzare le transazioni note

    try:
        # Recupera le transazioni iniziali per evitare notifiche su vecchie transazioni
        transactions = get_transactions(wallet_address)
        if isinstance(transactions, str):  # Gestione errore da get_transactions
            print(transactions)
            return
        for tx in transactions:
            known_transactions.add(tx['hash'])
    except Exception as e:
        print(f"Errore iniziale nel recupero delle transazioni: {e}")
        return

    while True:
        try:
            transactions = get_transactions(wallet_address)
            if isinstance(transactions, str):  # Gestione errore da get_transactions
                print(transactions)
                break

            for tx in transactions:
                tx_hash = tx['hash']
                # Ignora le transazioni già note
                if tx_hash in known_transactions:
                    continue

                # Ignora transazioni non confermate
                confirmations = tx.get("block_height")
                if confirmations is None:
                    print(f"Transazione {tx_hash} è ancora in pending. Ignorata.")
                    continue

                # Filtra le transazioni avvenute dopo l'inizio del monitoraggio
                if tx.get('time', 0) >= start_time:
                    known_transactions.add(tx_hash)  # Aggiungi alla lista di transazioni note

                    # Calcola l'importo totale in BTC
                    import decimal
                    total_value_btc = sum(
                        decimal.Decimal(out['value']) / decimal.Decimal(1e8)
                        for out in tx.get('out', [])
                    )

                    # Determina la direzione della transazione
                    is_outgoing = any(
                        inp['prev_out']['addr'] == wallet_address
                        for inp in tx.get('inputs', [])
                    )
                    direction = "Uscita" if is_outgoing else "Entrata"

                    # Prepara il messaggio
                    message = (
                        f"Nuova transazione rilevata per il wallet {wallet_address}:\n"
                        f"Direzione: {direction}\n"
                        f"Hash: {tx_hash}\n"
                        f"Data: {datetime.utcfromtimestamp(tx['time']).strftime('%d-%m-%Y %H:%M:%S')}\n"
                        f"Importo: {total_value_btc:.8f} BTC\n"
                        f"Conferme: Confermata\n"
                        f"Esplora: https://www.blockchain.com/btc/tx/{tx_hash}"
                    )

                    # Invia l'email
                    send_email(email, "Nuova transazione Bitcoin", message)

            time.sleep(15)  # Aspetta 15 secondi prima del prossimo controllo
        except Exception as e:
            print(f"Errore durante il monitoraggio: {e}")
            break

def is_valid_wallet(wallet_address):
    """
    Controlla se l'indirizzo del wallet Bitcoin è valido.
    """
    pattern = r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$'  # Base58 valida per Bitcoin
    return re.match(pattern, wallet_address) is not None

def is_valid_email(email):
    """
    Verifica se l'email fornita è valida.
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w{2,4}$'
    return re.match(pattern, email) is not None


# La pagina iniziale.
@app.route('/')
def home():
    return render_template('home.html')


# Endpoint per visualizzare la pagina
@app.route('/alert', methods=['GET'])
def alert_page():
    return render_template('page_two.html')


# Endpoint per avviare il monitoraggio
@app.route('/alert', methods=['POST'])
def alert():
    """
    Avvia il monitoraggio del wallet e invia notifiche email in caso di nuove transazioni.
    """
    wallet_address = request.form.get('wallet_address')
    email = request.form.get('email')

    # Verifica che l'indirizzo del wallet e l'email siano stati forniti
    if not wallet_address or not email:
        return render_template('page_two.html', error="Dati incompleti. Inserisci wallet ed email.")

    # Controllo indirizzo del wallet
    if not is_valid_wallet(wallet_address):
        return render_template(
            'page_two.html',
            error="L'indirizzo del wallet Bitcoin inserito non è valido. Controlla e riprova."
        )

    # Controllo email
    if not is_valid_email(email):
        return render_template(
            'page_two.html',
            error="L'indirizzo email inserito non è valido. Controlla e riprova."
        )

    try:
        # Recupero delle transazioni
        transactions = get_transactions(wallet_address)
        if transactions is None:
            return render_template(
                'page_two.html',
                error="Errore durante il recupero delle transazioni. Verifica la connessione o l'indirizzo fornito."
            )

        # Avvia il monitoraggio in un thread separato
        monitor_thread = threading.Thread(target=monitor_wallet, args=(wallet_address, email))
        monitor_thread.daemon = True  # Il thread si interrompe automaticamente alla chiusura del server
        monitor_thread.start()

        # Stampa un messaggio di log nella console
        print(f"Monitoraggio avviato per il wallet: {wallet_address}, email: {email}")

        # Renderizza il messaggio di successo
        return render_template(
            'page_two.html',
            success=f"Monitoraggio avviato con successo per il wallet {wallet_address}."
        )
    except Exception as e:
        print(f"Errore durante l'avvio del monitoraggio: {e}")
        return render_template(
            'page_two.html',
            error="Si è verificato un errore imprevisto durante l'avvio del monitoraggio. Riprova più tardi."
        )


# La pagina del Tracciamento di un wallet bitcoin - CONSULTAZIONE, REPORT, NO AVVISI
@app.route('/tracker', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        wallet_address = request.form['wallet_address']
        btc_to_eur_rate = get_btc_to_eur_rate()
        current_block_height = get_current_block_height()

        if btc_to_eur_rate is None or current_block_height is None:
            error = "Impossibile recuperare i dati necessari per la ricerca."
            return render_template('index.html', error=error, history=search_history)
        
        transactions = get_transactions(wallet_address)
        if isinstance(transactions, str):
            return render_template('index.html', error=transactions, history=search_history)
        
        parsed_transactions = [
            parse_transaction(tx, wallet_address, btc_to_eur_rate, current_block_height) 
            for tx in transactions[:50]
        ]
        
        # Analizza il cluster del wallet
        wallet_cluster = analyze_wallet_cluster(wallet_address)
        cluster_message = f"Appartiene al cluster: {wallet_cluster}" if wallet_cluster else "Nessun cluster noto rilevato."

        # Aggiunge il wallet alla cronologia
        if wallet_address not in search_history:
            search_history.append(wallet_address)

        # Genera i grafici con i dati completi
        combined_graph = generate_combined_flow_graph(wallet_address, parsed_transactions)
        inflow_graph = generate_separate_flow_graph(wallet_address, parsed_transactions, "Entrata")
        outflow_graph = generate_separate_flow_graph(wallet_address, parsed_transactions, "Uscita")

        return render_template(
            'index.html',
            wallet_address=wallet_address,
            transactions=parsed_transactions,
            cluster_message=cluster_message,
            combined_graph=combined_graph,
            inflow_graph=inflow_graph,
            outflow_graph=outflow_graph,
            history=search_history
        )

    # Filtraggio dei dati (richiesta GET)
    wallet_address = request.args.get('wallet_address')
    filter_direction = request.args.get('filter_direction')  # Recupero del filtro direzione
    price_range = request.args.get('filter_price')  # Recupero del filtro prezzo
    filter_status = request.args.get('filter_status')  # Recupero del filtro status
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if wallet_address:
        btc_to_eur_rate = get_btc_to_eur_rate()
        current_block_height = get_current_block_height()

        if btc_to_eur_rate is None or current_block_height is None:
            error = "Impossibile recuperare i dati necessari per la ricerca."
            return render_template('index.html', error=error, history=search_history)
        
        transactions = get_transactions(wallet_address)
        if isinstance(transactions, str):
            return render_template('index.html', error=transactions, history=search_history)
        
        parsed_transactions = [
            parse_transaction(tx, wallet_address, btc_to_eur_rate, current_block_height) 
            for tx in transactions[:50]
        ]

        # Applica i filtri
        filtered_transactions = filter_transactions(parsed_transactions, filter_direction, start_date, end_date, price_range, filter_status)

        # Genera i grafici con i dati filtrati
        combined_graph = generate_combined_flow_graph(wallet_address, filtered_transactions)
        inflow_graph = generate_separate_flow_graph(wallet_address, filtered_transactions, "Entrata")
        outflow_graph = generate_separate_flow_graph(wallet_address, filtered_transactions, "Uscita")

        # Analizza il cluster del wallet
        wallet_cluster = analyze_wallet_cluster(wallet_address)
        cluster_message = f"Appartiene al cluster: {wallet_cluster}" if wallet_cluster else "Nessun cluster noto rilevato."

        return render_template(
            'index.html',
            wallet_address=wallet_address,
            transactions=filtered_transactions,
            cluster_message=cluster_message,
            combined_graph=combined_graph,
            inflow_graph=inflow_graph,
            outflow_graph=outflow_graph,
            history=search_history
        )

    return render_template('index.html', history=search_history)

@app.route('/download_docx')
def download_docx():
    return send_file("static/wallet_report.docx", as_attachment=True)

@app.route('/download_excel')
def download_excel():
    return send_file("static/wallet_report.xlsx", as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True, threaded=False)

