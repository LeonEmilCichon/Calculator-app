from flask import Flask, request, jsonify, session, redirect
import json
import hashlib

app = Flask(__name__)
app.secret_key = "super_secret_key"

# ---------- LOAD USERS ----------
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

# ---------- HASH ----------
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ---------- SAFE CALCULATOR ----------
def safe_calc(expr):
    allowed = "0123456789+-*/(). "
    if any(c not in allowed for c in expr):
        return "Invalid"

    try:
        return str(eval(expr, {"__builtins__": None}, {}))
    except:
        return "Error"

# ---------- HTML ----------
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>App</title>
<style>
body {
    background: #0f172a;
    color: white;
    font-family: Arial;
    text-align: center;
}
.container {
    margin-top: 50px;
}
input {
    padding: 12px;
    margin: 5px;
    width: 220px;
    border-radius: 10px;
    border: none;
}
button {
    padding: 12px;
    border-radius: 10px;
    border: none;
    background: #22c55e;
    color: white;
    font-size: 16px;
}
.card {
    background: #1e293b;
    padding: 20px;
    border-radius: 20px;
    display: inline-block;
}
</style>
</head>
<body>

<div class="container">

<div class="card" id="auth">
<h2>🔐 Login / Register</h2>
<input id="user" placeholder="Username"><br>
<input id="pass" type="password" placeholder="Password"><br>
<button onclick="register()">Register</button>
<button onclick="login()">Login</button>
</div>

<div class="card" id="app" style="display:none;">
<h2>🧮 Calculator</h2>
<input id="expr" placeholder="5*10+2"><br>
<button onclick="calc()">Calculate</button>
<h3 id="res"></h3>
<button onclick="logout()">Logout</button>
</div>

</div>

<script>
function register() {
    fetch("/register", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            user: user.value,
            pass: pass.value
        })
    }).then(r=>r.json()).then(d=>alert(d.msg))
}

function login() {
    fetch("/login", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            user: user.value,
            pass: pass.value
        })
    }).then(r=>r.json()).then(d=>{
        if(d.ok){
            auth.style.display="none"
            app.style.display="block"
        } else alert("Login failed")
    })
}

function calc() {
    fetch("/calc", {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({expr: expr.value})
    }).then(r=>r.json()).then(d=>{
        res.innerText = d.result
    })
}

function logout(){
    fetch("/logout").then(()=>{
        location.reload()
    })
}
</script>

</body>
</html>
"""

# ---------- ROUTES ----------

@app.route("/")
def home():
    return HTML

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    users = load_users()

    if data["user"] in users:
        return jsonify({"msg": "User exists"})

    users[data["user"]] = hash_pw(data["pass"])
    save_users(users)

    return jsonify({"msg": "Registered!"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    users = load_users()

    if data["user"] in users and users[data["user"]] == hash_pw(data["pass"]):
        session["user"] = data["user"]
        return jsonify({"ok": True})

    return jsonify({"ok": False})

@app.route("/calc", methods=["POST"])
def calc():
    if "user" not in session:
        return jsonify({"result": "Login first"})

    expr = request.json["expr"]
    result = safe_calc(expr)
    return jsonify({"result": result})

@app.route("/logout")
def logout():
    session.clear()
    return "ok"

import os
app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
