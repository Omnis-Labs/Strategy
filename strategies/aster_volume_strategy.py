import requests
import hmac
import hashlib
import time
import urllib.parse
import decimal
import os
# import signal
import sys

# --- Default Strategy Parameters (Internal) ---
DEFAULT_ITERATIONS = 5
DEFAULT_DELAY_SECONDS = 1
DEFAULT_POLL_INTERVAL_SECONDS = 0.5
DEFAULT_MAX_POLL_ATTEMPTS = 20
# ORDER_QUANTITY will be calculated based on USDT amount
MIN_NOTIONAL_VALUE = decimal.Decimal("5") # Example minimum

# --- Get API Keys & Core Parameters from Environment Variables ---
API_KEY = os.environ.get("VAULT_API_KEY")
SECRET_KEY = os.environ.get("VAULT_SECRET_KEY")
TARGET_SYMBOL = os.environ.get("VAULT_SYMBOL")
USDT_AMOUNT_STR = os.environ.get("VAULT_USDT_AMOUNT")
# Optional: Allow overriding iterations via env var?
ITERATIONS_STR = os.environ.get("VAULT_ITERATIONS") # Keep default if not provided

# --- Validate Core Parameters ---
if not API_KEY or not SECRET_KEY: print("[ERROR] Keys missing.", file=sys.stderr); sys.exit(1)
if not TARGET_SYMBOL: print("[ERROR] Symbol missing.", file=sys.stderr); sys.exit(1)
if not USDT_AMOUNT_STR: print("[ERROR] USDT Amount missing.", file=sys.stderr); sys.exit(1)
try:
    USDT_AMOUNT = decimal.Decimal(USDT_AMOUNT_STR)
    if USDT_AMOUNT <= 0: raise ValueError("USDT amount must be positive.")
except Exception as e: print(f"[ERROR] Invalid USDT Amount: {e}", file=sys.stderr); sys.exit(1)

ITERATIONS = DEFAULT_ITERATIONS
if ITERATIONS_STR:
    try: ITERATIONS = int(ITERATIONS_STR); 
        if ITERATIONS < 1: raise ValueError()
    except ValueError: print(f"[WARN] Invalid VAULT_ITERATIONS '{ITERATIONS_STR}', using default {DEFAULT_ITERATIONS}.")

# Use other internal defaults
DELAY_SECONDS = DEFAULT_DELAY_SECONDS
POLL_INTERVAL_SECONDS = DEFAULT_POLL_INTERVAL_SECONDS
MAX_POLL_ATTEMPTS = DEFAULT_MAX_POLL_ATTEMPTS

# --- Constants & Precision ---
BASE_URL = "https://fapi.asterdex.com"
PRICE_PRECISION = decimal.Decimal('0.0001') # Needed for price fetch, not orders
QUANTITY_PRECISION = decimal.Decimal('1')
TICK_SIZE = decimal.Decimal('0.0001')

# --- API Functions (Identical to grid strategies) ---
def get_server_time():
    try: response = requests.get(f"{BASE_URL}/fapi/v1/time"); response.raise_for_status(); return response.json()['serverTime']
    except Exception as e: print(f"Error getting server time: {e}", file=sys.stderr); return None
def generate_signature(params_str):
    if not SECRET_KEY: print("[ERROR] No secret key.", file=sys.stderr); return None
    return hmac.new(SECRET_KEY.encode('utf-8'), params_str.encode('utf-8'), hashlib.sha256).hexdigest()
def make_signed_request(method, endpoint, params=None):
    if params is None: params = {}
    t = get_server_time();
    if t is None: return None
    pfs = params.copy(); pfs['timestamp']=int(t); pfs['recvWindow']=5000
    qs = urllib.parse.urlencode(sorted(pfs.items())); sig = generate_signature(qs)
    if sig is None: return None
    fqs = f"{qs}&signature={sig}"; url = f"{BASE_URL}{endpoint}?{fqs}"
    hdrs = {'X-MBX-APIKEY': API_KEY};
    if not API_KEY: print("[ERROR] No API key.", file=sys.stderr); return None
    try:
        if method.upper()=='GET': r=requests.get(url,headers=hdrs)
        elif method.upper()=='POST': r=requests.post(url,headers=hdrs)
        elif method.upper()=='DELETE': r=requests.delete(url,headers=hdrs)
        else: print(f"Unsupported method: {method}", file=sys.stderr); return None
        r.raise_for_status(); return r.json()
    except Exception as e: print(f"API Error {method} {endpoint}: {e}", file=sys.stderr);
        if hasattr(e, 'response') and e.response is not None: print(f" Resp: {e.response.text}", file=sys.stderr);
        return None
def get_current_price(symbol):
    # Public endpoint, no signing needed
    endpoint = "/fapi/v1/ticker/price"; params = {'symbol': symbol}
    try: r=requests.get(f"{BASE_URL}{endpoint}",params=params); r.raise_for_status(); return decimal.Decimal(r.json()['price'])
    except Exception as e: print(f"Error getting price {symbol}: {e}", file=sys.stderr); return None

# --- Volume Strategy Specific Functions ---
def place_market_order(symbol, side, quantity):
    endpoint = "/fapi/v1/order"
    try:
        formatted_quantity = quantity.quantize(QUANTITY_PRECISION, decimal.ROUND_DOWN)
        if formatted_quantity <= 0: print(f"[ERROR] Mkt Ord Qty <= 0 ({formatted_quantity}).", file=sys.stderr); return None
    except Exception as e: print(f"[ERROR] Format Mkt Ord Qty: {e}", file=sys.stderr); return None
    params = {'symbol': symbol, 'side': side.upper(), 'type': 'MARKET', 'quantity': str(formatted_quantity)}
    print(f"Placing MARKET {side} {formatted_quantity} {symbol.replace('USDT', '')}...")
    return make_signed_request('POST', endpoint, params)
def get_order_status(symbol, order_id):
    endpoint = "/fapi/v1/order"; params = {'symbol': symbol, 'orderId': str(order_id)}
    return make_signed_request('GET', endpoint, params)

# --- Main Execution ---
if __name__ == "__main__":

    # --- Calculate Order Quantity based on USDT Amount and Current Price ---
    print(f"Fetching current price for {TARGET_SYMBOL} to calculate order quantity...")
    current_price = get_current_price(TARGET_SYMBOL)
    if current_price is None or current_price <= 0:
        print(f"[ERROR] Could not fetch a valid current price for {TARGET_SYMBOL}. Exiting.", file=sys.stderr)
        sys.exit(1)
    
    # Calculate quantity: USDT / Price
    calculated_order_qty_precise = USDT_AMOUNT / current_price
    ORDER_QUANTITY = calculated_order_qty_precise.quantize(QUANTITY_PRECISION, decimal.ROUND_DOWN)
    
    print(f"[INFO] Current Price={current_price:.4f}, USDT Amount={USDT_AMOUNT} -> Calculated Order Qty={ORDER_QUANTITY}")

    # --- Sanity Checks ---
    if ORDER_QUANTITY <= 0:
        print(f"[ERROR] Calculated order quantity is zero or negative ({ORDER_QUANTITY}). USDT amount might be too low for the current price.", file=sys.stderr)
        sys.exit(1)
    min_notional_check = ORDER_QUANTITY * current_price # Approximate notional
    if min_notional_check < MIN_NOTIONAL_VALUE:
        print(f"[ERROR] Calculated order notional value ({min_notional_check:.4f} USDT) is below minimum required ({MIN_NOTIONAL_VALUE} USDT).", file=sys.stderr)
        sys.exit(1)
    # --------------------

    print(f"--- Market Order Volume Strategy Initializing (from Vault) ---")
    print(f"Symbol: {TARGET_SYMBOL}")
    print(f"USDT Amount Target per Trade: {USDT_AMOUNT}")
    print(f"==> Calculated Order Quantity per trade: {ORDER_QUANTITY} {TARGET_SYMBOL.replace('USDT','')}")
    print(f"Using Iterations: {ITERATIONS} (Default or from VAULT_ITERATIONS)")
    print(f"Using Delay: {DELAY_SECONDS}s, Poll Interval: {POLL_INTERVAL_SECONDS}s, Max Attempts: {MAX_POLL_ATTEMPTS}")
    print(f"Using Precisions: Qty={QUANTITY_PRECISION}")

    # --- Main Loop --- 
    for i in range(ITERATIONS):
        print(f"--- Cycle {i+1}/{ITERATIONS} --- commencing --- ")
        buy_filled, sell_filled = False, False
        buy_oid, sell_oid = None, None

        # --- 1. Place Market Buy Order --- 
        print(f"Placing BUY order...")
        buy_res = place_market_order(TARGET_SYMBOL, 'BUY', ORDER_QUANTITY)
        if buy_res and isinstance(buy_res, dict) and 'orderId' in buy_res:
            buy_oid = buy_res['orderId']
            print(f" BUY Placed. ID:{buy_oid}, Status:{buy_res.get('status')}")
            # --- 2. Poll for Buy Order Fill --- 
            print(f" Polling BUY {buy_oid}...")
            for attempt in range(MAX_POLL_ATTEMPTS):
                time.sleep(POLL_INTERVAL_SECONDS)
                status_res = get_order_status(TARGET_SYMBOL, buy_oid)
                if status_res and isinstance(status_res, dict):
                    stat = status_res.get('status')
                    if stat == 'FILLED': print(f" BUY {buy_oid} FILLED."); buy_filled=True; break
                    elif stat in ['CANCELED','EXPIRED','REJECTED','NEW']:
                         if stat != 'NEW' or attempt == MAX_POLL_ATTEMPTS-1:
                              print(f"[ERROR] BUY {buy_oid} failed/timeout. Status:{stat}", file=sys.stderr); buy_filled=False; break
                else: print(f" Poll {attempt+1}: Failed status for BUY {buy_oid}.")
            if not buy_filled: print(f"[ERROR] BUY {buy_oid} not filled. Skipping cycle.", file=sys.stderr); continue
        else: print(f"[ERROR] Failed to place BUY order: {buy_res}", file=sys.stderr); continue

        # --- 3. Place Market Sell Order --- 
        if buy_filled:
            print(f"Placing SELL order...")
            sell_res = place_market_order(TARGET_SYMBOL, 'SELL', ORDER_QUANTITY)
            if sell_res and isinstance(sell_res, dict) and 'orderId' in sell_res:
                sell_oid = sell_res['orderId']
                print(f" SELL Placed. ID:{sell_oid}, Status:{sell_res.get('status')}")
                # --- 4. Poll for Sell Order Fill --- 
                print(f" Polling SELL {sell_oid}...")
                for attempt in range(MAX_POLL_ATTEMPTS):
                    time.sleep(POLL_INTERVAL_SECONDS)
                    status_res = get_order_status(TARGET_SYMBOL, sell_oid)
                    if status_res and isinstance(status_res, dict):
                        stat = status_res.get('status')
                        if stat == 'FILLED': print(f" SELL {sell_oid} FILLED."); sell_filled=True; break
                        elif stat in ['CANCELED','EXPIRED','REJECTED','NEW']:
                            if stat != 'NEW' or attempt == MAX_POLL_ATTEMPTS-1:
                                 print(f"[ERROR] SELL {sell_oid} failed/timeout. Status:{stat}", file=sys.stderr); break
                    else: print(f" Poll {attempt+1}: Failed status for SELL {sell_oid}.")
                if not sell_filled: print(f"[ERROR] SELL {sell_oid} not filled.", file=sys.stderr)
            else: print(f"[ERROR] Failed to place SELL order: {sell_res}", file=sys.stderr)
        # --- End Cycle --- 
        state = "successfully" if buy_filled and sell_filled else "with errors"
        print(f"--- Cycle {i+1}/{ITERATIONS} completed {state}. Waiting {DELAY_SECONDS}s --- ")
        time.sleep(DELAY_SECONDS)
    # End main loop
    print("Strategy finished.") 