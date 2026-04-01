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
            "id
         f["id"],
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
        <title>Fristen & Aufgaben</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6f9;
                margin: 0;
                padding: 20px;
                color: #222;
            }

            h1, h2 {
                margin-top: 0;
            }

            .topbar {
                display: flex;
                gap: 12px;
                margin-bottom: 20px;
                flex-wrap: wrap;
            }

            .tab-btn {
                background: #fff;
                border: 2px solid #d0d7e2;
                border-radius: 14px;
                padding: 10px 18px;
                cursor: pointer;
                font-weight: bold;
                transition: 0.2s;
            }

            .tab-btn:hover {
                background: #eaf0ff;
            }

            .section {
                display: none;
            }

            .section.active {
                display: block;
            }

            .card {
                background: white;
                border-radius: 20px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.06);
            }

            input, select, textarea, button {
                padding: 10px;
                margin: 6px 0;
                border-radius: 12px;
                border: 1px solid #ccc;
                font-size: 14px;
                width: 100%;
                box-sizing: border-box;
            }

            textarea {
                min-height: 90px;
                resize: vertical;
            }

            button {
                background: #2f6fed;
                color: white;
                border: none;
                cursor: pointer;
                font-weight: bold;
            }

            button:hover {
                background: #1d56c4;
            }

            .small-btn {
                width: auto;
                padding: 8px 14px;
                font-size: 13px;
                border-radius: 10px;
            }

            .delete-btn {
                background: #d83c3c;
            }

            .delete-btn:hover {
                background: #b72e2e;
            }

            .done-btn {
                background: #1f9d5c;
            }

            .done-btn:hover {
                background: #187948;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                background: white;
                border-radius: 16px;
                overflow: hidden;
            }

            th, td {
                padding: 12px;
                border-bottom: 1px solid #eee;
                text-align: left;
                vertical-align: top;
            }

            th {
                background: #eef3ff;
            }

            .badge {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 999px;
                font-size: 13px;
                font-weight: bold;
            }

            .verstrichen {
                background: #ffd8d8;
                color: #b30000;
            }

            .dringend {
                background: #ffe3c4;
                color: #b35b00;
            }

            .bald {
                background: #fff3c9;
                color: #9b7a00;
            }

            .ausstehend {
                background: #d9f5df;
                color: #157a2f;
            }

            .erledigt {
                background: #d7e7ff;
                color: #2156b5;
            }

            .task-card {
                border: 1px solid #e1e6ef;
                border-radius: 18px;
                padding: 16px;
                margin-bottom: 16px;
                background: #fff;
            }

            details summary {
                cursor: pointer;
                font-weight: bold;
                margin-bottom: 10px;
            }

            .grid-2 {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 14px;
            }

            @media (max-width: 800px) {
                .grid-2 {
                    grid-template-columns: 1fr;
                }

                table {
                    display: block;
                    overflow-x: auto;
                }
            }
        </style>

        <script>
            function showTab(tabId) {
                document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');
            }
        </script>
    </head>
    <body>

        <h1>📁 Kanzlei Dashboard</h1>

        <div class="topbar">
            <button class="tab-btn" onclick="showTab('fristen')">Fristen</button>
            <button class="tab-btn" onclick="showTab('aufgaben')">Aufgaben</button>
            <button class="tab-btn" onclick="showTab('mitarbeiter')">Mitarbeiter</button>
        </div>

        <!-- FRISTEN -->
        <div id="fristen" class="section active">
            <div class="card">
                <h2>Neue Frist</h2>
                <form method="post" action="/add_frist">
                    <div class="grid-2">
                        <input name="name" placeholder="Frist / Bezeichnung" required>
                        <input type="date" name="datum" required>
                        <input name="aktenzeichen" placeholder="Aktenzeichen">
                        <select name="benutzer">
                            <option value="">Benutzer auswählen</option>
                            {% for m in mitarbeiter %}
                                <option value="{{ m['name'] }}">{{ m['name'] }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <button type="submit">Frist speichern</button>
                </form>
            </div>

            <div class="card">
                <h2>Fristenübersicht</h2>
                <table>
                    <tr>
                        <th>Frist</th>
                        <th>Datum</th>
                        <th>AZ</th>
                        <th>Benutzer</th>
                        <th>Tage</th>
                        <th>Status</th>
                        <th>Hinzugefügt</th>
                        <th>Aktion</th>
                    </tr>

                    {% for f in fristen %}
                    <tr>
                        <td>{{ f.name }}</td>
                        <td>{{ f.datum }}</td>
                        <td>{{ f.aktenzeichen }}</td>
                        <td>{{ f.benutzer }}</td>
                        <td>{{ f.tage }}</td>
                        <td>
                            {% if f.erledigt %}
                                <span class="badge erledigt">Erledigt</span>
                            {% else %}
                                <span class="badge {{ f.status_class }}">{{ f.status_text }}</span>
                            {% endif %}
                        </td>
                        <td>{{ f.erstellt_am }}</td>
                        <td>
                            {% if not f.erledigt %}
                            <form method="post" action="/toggle_frist/{{ f.id }}" style="display:inline;">
                                <button class="small-btn done-btn">Erledigt</button>
                            </form>
                            {% endif %}
                            <form method="post" action="/delete_frist/{{ f.id }}" style="display:inline;">
                                <button class="small-btn delete-btn" onclick="return confirm('Frist wirklich löschen?')">Löschen</button>
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
                    <div class="grid-2">
                        <select name="mitarbeiter">
                            <option value="">Mitarbeiter auswählen</option>
                            {% for m in mitarbeiter %}
                                <option value="{{ m['name'] }}">{{ m['name'] }}</option>
                            {% endfor %}
                        </select>
                        <input name="aktenzeichen" placeholder="Aktenzeichen">
                        <input name="senden_an" placeholder="Senden an">
                        <input name="versandweg" placeholder="Versandweg">
                    </div>

                    <textarea name="aufgabe" placeholder="Aufgabe" required></textarea>
                    <input name="anhang" placeholder="Anhang">
                    <textarea name="notizen" placeholder="Notizen"></textarea>

                    <button type="submit">Aufgabe speichern</button>
                </form>
            </div>

            <div class="card">
                <h2>Aufgabenübersicht</h2>

                {% for a in aufgaben %}
                <div class="task-card">
                    <details>
                        <summary>
                            {{ a['mitarbeiter'] or 'Kein Mitarbeiter' }} – {{ a['aufgabe'][:50] }}
                            {% if a['erledigt'] %}
                                <span class="badge erledigt">Erledigt</span>
                            {% else %}
                                <span class="badge ausstehend">Offen</span>
                            {% endif %}
                        </summary>

                        <p><b>Aktenzeichen:</b> {{ a['aktenzeichen'] }}</p>
                        <p><b>Senden an:</b> {{ a['senden_an'] }}</p>
                        <p><b>Versandweg:</b> {{ a['versandweg'] }}</p>
                        <p><b>Aufgabe:</b><br>{{ a['aufgabe'] }}</p>
                        <p><b>Anhang:</b> {{ a['anhang'] }}</p>
                        <p><b>Notizen:</b><br>{{ a['notizen'] }}</p>
                        <p><b>Hinzugefügt:</b> {{ a['erstellt_am'] }}</p>

                        {% if not a['erledigt'] %}
                        <form method="post" action="/toggle_aufgabe/{{ a['id'] }}" style="display:inline;">
                            <button class="small-btn done-btn">Erledigt</button>
                        </form>
                        {% endif %}
                        <form method="post" action="/delete_aufgabe/{{ a['id'] }}" style="display:inline;">
                            <button class="small-btn delete-btn" onclick="return confirm('Aufgabe wirklich löschen?')">Löschen</button>
                        </form>
                    </details>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- MITARBEITER -->
        <div id="mitarbeiter" class="section">
            <div class="card">
                <h2>Mitarbeiter verwalten</h2>
                <form method="post" action="/add_mitarbeiter">
                    <input name="name" placeholder="Neuer Mitarbeiter" required>
                    <button type="submit">Mitarbeiter hinzufügen</button>
                </form>
            </div>

            <div class="card">
                <h2>Vorhandene Mitarbeiter</h2>
                <table>
                    <tr>
                        <th>Name</th>
                        <th>Aktion</th>
                    </tr>
                    {% for m in mitarbeiter %}
                    <tr>
                        <td>{{ m['name'] }}</td>
                        <td>
                            <form method="post" action="/delete_mitarbeiter/{{ m['id'] }}">
                                <button class="small-btn delete-btn" onclick="return confirm('Mitarbeiter löschen?')">Löschen</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
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
