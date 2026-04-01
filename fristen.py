from flask import Flask, request, redirect, render_template_string
from datetime import datetime

app = Flask(__name__)

fristen = []
aufgaben = []
mitarbeiter = ["Praktikanten", "Herr Manouchehri"]


BASE_STYLE = """
<style>
    * { box-sizing: border-box; }

    body {
        font-family: Arial, sans-serif;
        background: #eef2f7;
        margin: 0;
        padding: 32px;
        color: #111827;
    }

    .container {
        max-width: 1500px;
        margin: auto;
    }

    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        gap: 20px;
        flex-wrap: wrap;
    }

    .title-wrap h1 {
        margin: 0;
        font-size: 34px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }

    .subtitle {
        margin-top: 8px;
        color: #6b7280;
        font-size: 15px;
    }

    .nav {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }

    .nav a {
        text-decoration: none;
        padding: 12px 16px;
        border-radius: 14px;
        font-weight: 800;
        background: white;
        color: #111827;
        border: 2px solid #dbe3ee;
        box-shadow: 0 6px 16px rgba(15, 23, 42, 0.05);
    }

    .nav a.active {
        background: #2563eb;
        color: white;
        border-color: #2563eb;
    }

    .card {
        background: white;
        border: 2px solid #dbe3ee;
        border-radius: 24px;
        padding: 24px;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
        margin-bottom: 24px;
    }

    .card h2 {
        margin-top: 0;
        margin-bottom: 18px;
        font-size: 22px;
    }

    form {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 14px;
        align-items: end;
    }

    .field {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .field label {
        font-size: 13px;
        font-weight: 700;
        color: #374151;
    }

    input, textarea, select {
        width: 100%;
        padding: 14px 16px;
        font-size: 15px;
        border-radius: 14px;
        border: 2px solid #d1d5db;
        background: #f9fafb;
        outline: none;
        transition: 0.2s;
    }

    textarea {
        resize: vertical;
        min-height: 90px;
    }

    input:focus, textarea:focus, select:focus {
        border-color: #2563eb;
        background: white;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.10);
    }

    button {
        padding: 14px 20px;
        border: none;
        border-radius: 14px;
        background: #2563eb;
        color: white;
        font-size: 15px;
        font-weight: 800;
        cursor: pointer;
        transition: 0.2s;
    }

    button:hover {
        background: #1d4ed8;
        transform: translateY(-1px);
    }

    .small-btn {
        padding: 10px 14px;
        font-size: 14px;
        border-radius: 12px;
    }

    .stats {
        display: flex;
        gap: 14px;
        flex-wrap: wrap;
    }

    .stat-box {
        background: white;
        border: 2px solid #dbe3ee;
        border-radius: 18px;
        padding: 16px 20px;
        min-width: 140px;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
    }

    .stat-label {
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 6px;
    }

    .stat-value {
        font-size: 24px;
        font-weight: 800;
    }

    .table-wrap {
        overflow-x: auto;
    }

    table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0 12px;
    }

    th {
        text-align: left;
        font-size: 13px;
        color: #6b7280;
        padding: 0 14px 8px 14px;
        font-weight: 800;
    }

    td {
        background: white;
        padding: 18px 14px;
        font-size: 15px;
        vertical-align: middle;
        border-top: 2px solid #e5e7eb;
        border-bottom: 2px solid #e5e7eb;
    }

    td:first-child {
        border-left: 2px solid #e5e7eb;
        border-top-left-radius: 18px;
        border-bottom-left-radius: 18px;
    }

    td:last-child {
        border-right: 2px solid #e5e7eb;
        border-top-right-radius: 18px;
        border-bottom-right-radius: 18px;
    }

    tr.done-row td {
        background: #f3f4f6;
        opacity: 0.78;
    }

    .badge {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 800;
        border: 1px solid transparent;
    }

    .verstrichen { background: #fee2e2; color: #b91c1c; border-color: #fecaca; }
    .dringend { background: #ffedd5; color: #c2410c; border-color: #fed7aa; }
    .bald { background: #fef3c7; color: #b45309; border-color: #fde68a; }
    .ausstehend { background: #dcfce7; color: #15803d; border-color: #bbf7d0; }
    .erledigt { background: #dbeafe; color: #1d4ed8; border-color: #bfdbfe; }

    .az {
        font-family: monospace;
        font-size: 14px;
        background: #f3f4f6;
        padding: 8px 10px;
        border-radius: 12px;
        display: inline-block;
        border: 1px solid #e5e7eb;
    }

    .user-tag {
        background: #ede9fe;
        color: #6d28d9;
        padding: 8px 12px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 800;
        display: inline-block;
    }

    .action-btn {
        text-decoration: none;
        font-weight: 800;
        font-size: 14px;
        padding: 10px 14px;
        border-radius: 12px;
        border: 2px solid #e5e7eb;
        transition: 0.2s;
        display: inline-block;
        margin-right: 8px;
        margin-bottom: 8px;
    }

    .done-btn { color: #059669; background: #ecfdf5; }
    .done-btn:hover { border-color: #10b981; background: #d1fae5; }
    .delete-btn { color: #dc2626; background: #fef2f2; }
    .delete-btn:hover { border-color: #ef4444; background: #fee2e2; }

    .task-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
        gap: 18px;
    }

    .task-card {
        background: white;
        border: 2px solid #dbe3ee;
        border-radius: 22px;
        padding: 20px;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.05);
    }

    .task-card.done {
        opacity: 0.7;
        background: #f3f4f6;
    }

    details summary {
        cursor: pointer;
        list-style: none;
        font-weight: 800;
        font-size: 16px;
        margin-bottom: 8px;
    }

    details summary::-webkit-details-marker {
        display: none;
    }

    .task-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 12px 0;
    }

    .task-field {
        margin-bottom: 10px;
        font-size: 14px;
        line-height: 1.6;
    }

    .task-field strong {
        color: #374151;
    }

    .employee-list {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-bottom: 18px;
    }

    .employee-chip {
        padding: 10px 14px;
        border-radius: 999px;
        background: white;
        border: 2px solid #dbe3ee;
        text-decoration: none;
        font-weight: 800;
        color: #111827;
    }

    .employee-chip.active {
        background: #2563eb;
        color: white;
        border-color: #2563eb;
    }

    .employee-row {
        display: flex;
        gap: 10px;
        align-items: center;
        flex-wrap: wrap;
        margin-bottom: 18px;
    }

    .empty {
        padding: 40px;
        text-align: center;
        color: #6b7280;
        background: #f9fafb;
        border: 2px dashed #d1d5db;
        border-radius: 20px;
        font-size: 16px;
    }

    @media (max-width: 1100px) {
        form { grid-template-columns: 1fr 1fr; }
    }

    @media (max-width: 700px) {
        body { padding: 18px; }
        .card { padding: 18px; border-radius: 18px; }
        form { grid-template-columns: 1fr; }
        .topbar { flex-direction: column; align-items: stretch; }
    }
</style>
"""


# ========================
# FRISTEN
# ========================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        hinzugefuegt = datetime.now().strftime("%d.%m.%Y %H:%M")
        fristen.append({
            "name": request.form["name"],
            "aktenzeichen": request.form["aktenzeichen"],
            "benutzer": request.form["benutzer"],
            "datum": request.form["datum"],
            "hinzugefuegt": hinzugefuegt,
            "erledigt": False
        })
        return redirect("/")

    heute = datetime.today()
    for f in fristen:
        f["tage"] = (datetime.strptime(f["datum"], "%Y-%m-%d") - heute).days

    sortiert = sorted(fristen, key=lambda x: (x["erledigt"], x["tage"]))

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Fristenkalender</title>
        """ + BASE_STYLE + """
    </head>
    <body>
        <div class="container">
            <div class="topbar">
                <div class="title-wrap">
                    <h1>📅 Kanzlei Dashboard</h1>
                    <div class="subtitle">Fristen- und Aufgabenübersicht für den Kanzlei-Alltag</div>
                </div>

                <div class="nav">
                    <a class="active" href="/">Fristen</a>
                    <a href="/aufgaben">Aufgaben</a>
                </div>
            </div>

            <div class="stats">
                <div class="stat-box"><div class="stat-label">Gesamt</div><div class="stat-value">{{ fristen|length }}</div></div>
                <div class="stat-box"><div class="stat-label">Offen</div><div class="stat-value">{{ fristen|selectattr('erledigt', 'equalto', False)|list|length }}</div></div>
                <div class="stat-box"><div class="stat-label">Erledigt</div><div class="stat-value">{{ fristen|selectattr('erledigt', 'equalto', True)|list|length }}</div></div>
            </div>

            <div class="card">
                <h2>Neue Frist anlegen</h2>
                <form method="post">
                    <div class="field">
                        <label>Frist / Vorgang</label>
                        <input type="text" name="name" required>
                    </div>

                    <div class="field">
                        <label>Aktenzeichen</label>
                        <input type="text" name="aktenzeichen" required>
                    </div>

                    <div class="field">
                        <label>Zuständig</label>
                        <input type="text" name="benutzer" required>
                    </div>

                    <div class="field">
                        <label>Fällig am</label>
                        <input type="date" name="datum" required>
                    </div>

                    <button type="submit">+ Hinzufügen</button>
                </form>
            </div>

            <div class="card">
                <h2>Aktuelle Fristen</h2>

                {% if fristen %}
                <div class="table-wrap">
                    <table>
                        <tr>
                            <th>Frist</th>
                            <th>Aktenzeichen</th>
                            <th>Zuständig</th>
                            <th>Fällig am</th>
                            <th>Tage</th>
                            <th>Status</th>
                            <th>Hinzugefügt</th>
                            <th>Aktion</th>
                        </tr>
                        {% for f in fristen %}
                        <tr class="{% if f.erledigt %}done-row{% endif %}">
                            <td><strong>{{ f.name }}</strong></td>
                            <td><span class="az">{{ f.aktenzeichen }}</span></td>
                            <td><span class="user-tag">{{ f.benutzer }}</span></td>
                            <td>{{ f.datum }}</td>
                            <td><strong>{{ f.tage }}</strong></td>
                            <td>
                                {% if f.erledigt %}
                                    <span class="badge erledigt">Erledigt</span>
                                {% elif f.tage < 0 %}
                                    <span class="badge verstrichen">Frist verstrichen</span>
                                {% elif f.tage <= 2 %}
                                    <span class="badge dringend">Dringend</span>
                                {% elif f.tage <= 5 %}
                                    <span class="badge bald">Bald bearbeiten</span>
                                {% else %}
                                    <span class="badge ausstehend">Ausstehend</span>
                                {% endif %}
                            </td>
                            <td>{{ f.hinzugefuegt }}</td>
                            <td>
                                {% if not f.erledigt %}
                                    <a class="action-btn done-btn" href="/done_frist/{{ loop.index0 }}">Erledigt</a>
                                {% endif %}
                                <a class="action-btn delete-btn" href="/delete_frist/{{ loop.index0 }}">Löschen</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
                {% else %}
                    <div class="empty">Noch keine Fristen vorhanden.</div>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """, fristen=sortiert)


# ========================
# AUFGABEN
# ========================
@app.route("/aufgaben", methods=["GET", "POST"])
def aufgaben_view():
    if request.method == "POST":
        hinzugefuegt = datetime.now().strftime("%d.%m.%Y %H:%M")
        aufgaben.append({
            "datum": request.form["datum"],
            "mitarbeiter": request.form["mitarbeiter"],
            "aktenzeichen": request.form["aktenzeichen"],
            "senden_an": request.form["senden_an"],
            "versand": request.form["versand"],
            "aufgabe": request.form["aufgabe"],
            "anhang": request.form["anhang"],
            "notizen": request.form["notizen"],
            "hinzugefuegt": hinzugefuegt,
            "erledigt": False
        })
        return redirect("/aufgaben")

    filter_user = request.args.get("user", "")
    gefiltert = [a for a in aufgaben if not filter_user or a["mitarbeiter"] == filter_user]
    sortiert = sorted(gefiltert, key=lambda x: (x["erledigt"], x["datum"]))

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Aufgaben</title>
        """ + BASE_STYLE + """
    </head>
    <body>
        <div class="container">
            <div class="topbar">
                <div class="title-wrap">
                    <h1>🗂 Aufgabenbereich</h1>
                    <div class="subtitle">Tagesbezogene Aufgaben nach Mitarbeiter, Versand und Vorgang</div>
                </div>

                <div class="nav">
                    <a href="/">Fristen</a>
                    <a class="active" href="/aufgaben">Aufgaben</a>
                </div>
            </div>

            <div class="stats">
                <div class="stat-box"><div class="stat-label">Aufgaben</div><div class="stat-value">{{ aufgaben|length }}</div></div>
                <div class="stat-box"><div class="stat-label">Mitarbeiter</div><div class="stat-value">{{ mitarbeiter|length }}</div></div>
                <div class="stat-box"><div class="stat-label">Offen</div><div class="stat-value">{{ aufgaben|selectattr('erledigt', 'equalto', False)|list|length }}</div></div>
            </div>

            <div class="card">
                <h2>Mitarbeiter verwalten</h2>

                <div class="employee-row">
                    <form method="post" action="/add_mitarbeiter" style="grid-template-columns: 1fr auto;">
                        <div class="field">
                            <label>Neuen Mitarbeiter hinzufügen</label>
                            <input type="text" name="name" placeholder="Name eingeben" required>
                        </div>
                        <button type="submit">+ Hinzufügen</button>
                    </form>
                </div>

                <div class="employee-list">
                    <a class="employee-chip {% if not filter_user %}active{% endif %}" href="/aufgaben">Alle</a>
                    {% for m in mitarbeiter %}
                        <a class="employee-chip {% if filter_user == m %}active{% endif %}" href="/aufgaben?user={{ m }}">{{ m }}</a>
                        <a class="action-btn delete-btn small-btn" href="/delete_mitarbeiter/{{ m }}" onclick="return confirm('Mitarbeiter wirklich entfernen?')">✕</a>
                    {% endfor %}
                </div>
            </div>

            <div class="card">
                <h2>Neue Aufgabe anlegen</h2>
                <form method="post" style="grid-template-columns: repeat(3, 1fr);">
                    <div class="field">
                        <label>Datum</label>
                        <input type="date" name="datum" required>
                    </div>

                    <div class="field">
                        <label>Mitarbeiter</label>
                        <select name="mitarbeiter" required>
                            {% for m in mitarbeiter %}
                                <option value="{{ m }}">{{ m }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <div class="field">
                        <label>Aktenzeichen</label>
                        <input type="text" name="aktenzeichen">
                    </div>

                    <div class="field">
                        <label>Senden an</label>
                        <input type="text" name="senden_an">
                    </div>

                    <div class="field">
                        <label>Versandweg</label>
                        <input type="text" name="versand">
                    </div>

                    <div class="field">
                        <label>Aufgabe</label>
                        <input type="text" name="aufgabe" required>
                    </div>

                    <div class="field">
                        <label>Anhang</label>
                        <input type="text" name="anhang">
                    </div>

                    <div class="field" style="grid-column: span 2;">
                        <label>Notizen</label>
                        <textarea name="notizen"></textarea>
                    </div>

                    <button type="submit">+ Aufgabe speichern</button>
                </form>
            </div>

            <div class="card">
                <h2>Aufgabenübersicht {% if filter_user %}für {{ filter_user }}{% endif %}</h2>

                {% if aufgaben %}
                <div class="task-grid">
                    {% for a in aufgaben %}
                    <div class="task-card {% if a.erledigt %}done{% endif %}">
                        <details>
                            <summary>{{ a.datum }} | {{ a.mitarbeiter }} | {{ a.aufgabe }}</summary>

                            <div class="task-meta">
                                <span class="az">{{ a.aktenzeichen or 'Kein AZ' }}</span>
                                <span class="user-tag">{{ a.mitarbeiter }}</span>
                                {% if a.erledigt %}
                                    <span class="badge erledigt">Erledigt</span>
                                {% else %}
                                    <span class="badge ausstehend">Offen</span>
                                {% endif %}
                            </div>

                            <div class="task-field"><strong>Senden an:</strong> {{ a.senden_an or '-' }}</div>
                            <div class="task-field"><strong>Versandweg:</strong> {{ a.versand or '-' }}</div>
                            <div class="task-field"><strong>Anhang:</strong> {{ a.anhang or '-' }}</div>
                            <div class="task-field"><strong>Notizen:</strong><br>{{ a.notizen or '-' }}</div>
                            <div class="task-field"><strong>Hinzugefügt:</strong> {{ a.hinzugefuegt }}</div>

                            <div style="margin-top: 14px;">
                                {% if not a.erledigt %}
                                    <a class="action-btn done-btn" href="/done_aufgabe/{{ loop.index0 }}">Erledigt</a>
                                {% endif %}
                                <a class="action-btn delete-btn" href="/delete_aufgabe/{{ loop.index0 }}">Löschen</a>
                            </div>
                        </details>
                    </div>
                    {% endfor %}
                </div>
                {% else %}
                    <div class="empty">Noch keine Aufgaben vorhanden.</div>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """, aufgaben=sortiert, mitarbeiter=mitarbeiter, filter_user=filter_user)


# ========================
# MITARBEITER
# ========================
@app.route("/add_mitarbeiter", methods=["POST"])
def add_mitarbeiter():
    name = request.form["name"].strip()
    if name and name not in mitarbeiter:
        mitarbeiter.append(name)
    return redirect("/aufgaben")


@app.route("/delete_mitarbeiter/<name>")
def delete_mitarbeiter(name):
    if name in mitarbeiter:
        mitarbeiter.remove(name)
    return redirect("/aufgaben")


# ========================
# FRISTEN AKTIONEN
# ========================
@app.route("/done_frist/<int:index>")
def done_frist(index):
    if 0 <= index < len(fristen):
        fristen[index]["erledigt"] = True
    return redirect("/")


@app.route("/delete_frist/<int:index>")
def delete_frist(index):
    if 0 <= index < len(fristen):
        fristen.pop(index)
    return redirect("/")


# ========================
# AUFGABEN AKTIONEN
# ========================
@app.route("/done_aufgabe/<int:index>")
def done_aufgabe(index):
    if 0 <= index < len(aufgaben):
        aufgaben[index]["erledigt"] = True
    return redirect("/aufgaben")


@app.route("/delete_aufgabe/<int:index>")
def delete_aufgabe(index):
    if 0 <= index < len(aufgaben):
        aufgaben.pop(index)
    return redirect("/aufgaben")


if __name__ == "__main__":
    app.run(debug=True)
