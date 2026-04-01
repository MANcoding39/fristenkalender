from flask import Flask, request, redirect, render_template_string
from datetime import datetime
import sqlite3

app = Flask(__name__)

# ---------------- DB ----------------
def get_db():
    conn = sqlite3.connect("data.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS mitarbeiter (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS fristen (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        datum TEXT NOT NULL,
        aktenzeichen TEXT,
        benutzer TEXT,
        erstellt_am TEXT,
        erledigt INTEGER DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS aufgaben (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mitarbeiter TEXT,
        aktenzeichen TEXT,
        senden_an TEXT,
        versandweg TEXT,
        aufgabe TEXT,
        anhang TEXT,
        notizen TEXT,
        erstellt_am TEXT,
        erledigt INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- HILFSFUNKTION ----------------
def berechne_status(datum):
    heute = datetime.today().date()
    ziel = datetime.strptime(datum, "%Y-%m-%d").date()
    tage = (ziel - heute).days

    if tage < 0:
        return "Frist verstrichen", "verstrichen", tage
    elif tage <= 2:
        return "Dringend", "dringend", tage
    elif tage <= 5:
        return "Bald bearbeiten", "bald", tage
    else:
        return "Ausstehend", "ausstehend", tage

# ---------------- HAUPTSEITE ----------------
@app.route("/", methods=["GET"])
def index():
    conn = get_db()
    c = conn.cursor()

    fristen = c.execute("SELECT * FROM fristen ORDER BY datum ASC").fetchall()
    mitarbeiter = c.execute("SELECT * FROM mitarbeiter ORDER BY name ASC").fetchall()
    aufgaben = c.execute("SELECT * FROM aufgaben ORDER BY id DESC").fetchall()

    conn.close()

    fristen_liste = []
    for f in fristen:
        status_text, status_class, tage = berechne_status(f["datum"])
        fristen_liste.append({
            "id": f["id"],
            "name": f["name"],
            "datum": f["datum"],
            "aktenzeichen": f["aktenzeichen"],
            "benutzer": f["benutzer"],
            "erstellt_am": f["erstellt_am"],
            "erledigt": f["erledigt"],
            "status_text": status_text,
            "status_class": status_class,
            "tage": tage
        })

   html = """
<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Kanzlei Dashboard</title>

<style>
body {
    font-family: 'Segoe UI', sans-serif;
    margin: 0;
    background: linear-gradient(135deg, #0f172a, #1e293b);
    color: #e2e8f0;
}

h1 {
    text-align: center;
    margin-bottom: 20px;
}

.topbar {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-bottom: 20px;
}

.tab-btn {
    padding: 10px 20px;
    border-radius: 12px;
    border: none;
    background: rgba(255,255,255,0.08);
    color: white;
    cursor: pointer;
    transition: 0.2s;
}

.tab-btn:hover {
    background: rgba(255,255,255,0.2);
}

.tab-btn.active {
    background: #3b82f6;
}

.section {
    display: none;
}

.section.active {
    display: block;
}

.card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 20px;
    margin: 20px auto;
    width: 90%;
    max-width: 1100px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

input, select, textarea, button {
    width: 100%;
    padding: 10px;
    border-radius: 10px;
    border: none;
    margin: 5px 0;
    background: rgba(255,255,255,0.1);
    color: white;
}

button {
    background: #3b82f6;
    cursor: pointer;
    font-weight: bold;
}

button:hover {
    background: #2563eb;
}

.small-btn {
    width: auto;
    padding: 6px 12px;
}

.delete-btn {
    background: #ef4444;
}

.done-btn {
    background: #22c55e;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.1);
}

.badge {
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 12px;
}

.verstrichen { background: #7f1d1d; }
.dringend { background: #9a3412; }
.bald { background: #854d0e; }
.ausstehend { background: #065f46; }
.erledigt { background: #1e40af; }

.task-card {
    background: rgba(255,255,255,0.06);
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
}

details summary {
    cursor: pointer;
    font-weight: bold;
}

.footer {
    position: fixed;
    bottom: 10px;
    right: 15px;
    font-size: 12px;
    opacity: 0.7;
}
</style>

<script>
function showTab(tabId, el) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    el.classList.add('active');
}
</script>

</head>
<body>

<h1>⚖️ Kanzlei Dashboard</h1>

<div class="topbar">
    <button class="tab-btn active" onclick="showTab('fristen', this)">Fristen</button>
    <button class="tab-btn" onclick="showTab('aufgaben', this)">Aufgaben</button>
    <button class="tab-btn" onclick="showTab('mitarbeiter', this)">Mitarbeiter</button>
</div>

<!-- FRISTEN -->
<div id="fristen" class="section active">
<div class="card">
<h2>Neue Frist</h2>
<form method="post" action="/add_frist">
<input name="name" placeholder="Bezeichnung" required>
<input type="date" name="datum" required>
<input name="aktenzeichen" placeholder="Aktenzeichen">
<select name="benutzer">
<option value="">Benutzer</option>
{% for m in mitarbeiter %}
<option value="{{ m['name'] }}">{{ m['name'] }}</option>
{% endfor %}
</select>
<button>Speichern</button>
</form>
</div>

<div class="card">
<h2>Fristen</h2>
<table>
<tr>
<th>Frist</th><th>Datum</th><th>AZ</th><th>Status</th><th>Aktion</th>
</tr>

{% for f in fristen %}
<tr>
<td>{{ f.name }}</td>
<td>{{ f.datum }}</td>
<td>{{ f.aktenzeichen }}</td>
<td>
{% if f.erledigt %}
<span class="badge erledigt">Erledigt</span>
{% else %}
<span class="badge {{ f.status_class }}">{{ f.status_text }}</span>
{% endif %}
</td>
<td>
<form method="post" action="/toggle_frist/{{ f.id }}">
<button class="small-btn done-btn">✔</button>
</form>
<form method="post" action="/delete_frist/{{ f.id }}">
<button class="small-btn delete-btn">✖</button>
</form>
</td>
</tr>
{% endfor %}

</table>
</div>
</div>

<!-- AUFGABEN -->
<div id="aufgaben" class="section">
<div class="card">
<h2>Neue Aufgabe</h2>
<form method="post" action="/add_aufgabe">
<select name="mitarbeiter">
<option>Mitarbeiter</option>
{% for m in mitarbeiter %}
<option value="{{ m['name'] }}">{{ m['name'] }}</option>
{% endfor %}
</select>

<input name="aktenzeichen" placeholder="Aktenzeichen">
<input name="senden_an" placeholder="Senden an">
<input name="versandweg" placeholder="Versandweg">
<textarea name="aufgabe" placeholder="Aufgabe" required></textarea>
<input name="anhang" placeholder="Anhang">
<textarea name="notizen" placeholder="Notizen"></textarea>

<button>Speichern</button>
</form>
</div>

<div class="card">
<h2>Aufgaben</h2>

{% for a in aufgaben %}
<div class="task-card">
<details>
<summary>{{ a['mitarbeiter'] }} – {{ a['aufgabe'][:40] }}</summary>

<p><b>AZ:</b> {{ a['aktenzeichen'] }}</p>
<p><b>Aufgabe:</b> {{ a['aufgabe'] }}</p>
<p><b>Notizen:</b> {{ a['notizen'] }}</p>

<form method="post" action="/toggle_aufgabe/{{ a['id'] }}">
<button class="small-btn done-btn">Erledigt</button>
</form>

<form method="post" action="/delete_aufgabe/{{ a['id'] }}">
<button class="small-btn delete-btn">Löschen</button>
</form>

</details>
</div>
{% endfor %}

</div>
</div>

<!-- MITARBEITER -->
<div id="mitarbeiter" class="section">
<div class="card">
<h2>Mitarbeiter</h2>
<form method="post" action="/add_mitarbeiter">
<input name="name" placeholder="Name">
<button>Hinzufügen</button>
</form>

{% for m in mitarbeiter %}
<p>
{{ m['name'] }}
<form method="post" action="/delete_mitarbeiter/{{ m['id'] }}">
<button class="small-btn delete-btn">X</button>
</form>
</p>
{% endfor %}
</div>
</div>

<div class="footer">
© Copyright by Fabian Ziems
</div>

</body>
</html>
"""

    return render_template_string(html, fristen=fristen_liste, mitarbeiter=mitarbeiter, aufgaben=aufgaben)

# ---------------- FRISTEN ----------------
@app.route("/add_frist", methods=["POST"])
def add_frist():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        INSERT INTO fristen (name, datum, aktenzeichen, benutzer, erstellt_am)
        VALUES (?, ?, ?, ?, ?)
    """, (
        request.form["name"],
        request.form["datum"],
        request.form["aktenzeichen"],
        request.form["benutzer"],
        datetime.now().strftime("%d.%m.%Y %H:%M")
    ))

    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete_frist/<int:id>", methods=["POST"])
def delete_frist(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM fristen WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/toggle_frist/<int:id>", methods=["POST"])
def toggle_frist(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE fristen SET erledigt = 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

# ---------------- AUFGABEN ----------------
@app.route("/add_aufgabe", methods=["POST"])
def add_aufgabe():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        INSERT INTO aufgaben (mitarbeiter, aktenzeichen, senden_an, versandweg, aufgabe, anhang, notizen, erstellt_am)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        request.form["mitarbeiter"],
        request.form["aktenzeichen"],
        request.form["senden_an"],
        request.form["versandweg"],
        request.form["aufgabe"],
        request.form["anhang"],
        request.form["notizen"],
        datetime.now().strftime("%d.%m.%Y %H:%M")
    ))

    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete_aufgabe/<int:id>", methods=["POST"])
def delete_aufgabe(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM aufgaben WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/toggle_aufgabe/<int:id>", methods=["POST"])
def toggle_aufgabe(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE aufgaben SET erledigt = 1 WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

# ---------------- MITARBEITER ----------------
@app.route("/add_mitarbeiter", methods=["POST"])
def add_mitarbeiter():
    conn = get_db()
    c = conn.cursor()
    c.execute("INSERT INTO mitarbeiter (name) VALUES (?)", (request.form["name"],))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete_mitarbeiter/<int:id>", methods=["POST"])
def delete_mitarbeiter(id):
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM mitarbeiter WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
