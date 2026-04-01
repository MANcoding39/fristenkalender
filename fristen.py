from flask import Flask, request, redirect, render_template_string
from datetime import datetime

app = Flask(__name__)

fristen = []


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        aktenzeichen = request.form["aktenzeichen"]
        benutzer = request.form["benutzer"]
        datum = request.form["datum"]
        hinzugefuegt = datetime.now().strftime("%d.%m.%Y %H:%M")

        fristen.append({
            "name": name,
            "aktenzeichen": aktenzeichen,
            "benutzer": benutzer,
            "datum": datum,
            "hinzugefuegt": hinzugefuegt,
            "erledigt": False
        })
        return redirect("/")

    heute = datetime.today()

    for f in fristen:
        f["datum_obj"] = datetime.strptime(f["datum"], "%Y-%m-%d")
        f["tage"] = (f["datum_obj"] - heute).days

    sortiert = sorted(fristen, key=lambda x: (x["erledigt"], x["tage"]))

    html = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Fristenkalender</title>
        <style>
            * {
                box-sizing: border-box;
            }

            body {
                font-family: Arial, sans-serif;
                background: #eef2f7;
                margin: 0;
                padding: 32px;
                color: #111827;
            }

            .container {
                max-width: 1450px;
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
                grid-template-columns: 2fr 1.3fr 1.3fr 1.2fr auto;
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

            input {
                width: 100%;
                padding: 14px 16px;
                font-size: 15px;
                border-radius: 14px;
                border: 2px solid #d1d5db;
                background: #f9fafb;
                outline: none;
                transition: 0.2s;
            }

            input:focus {
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
                min-width: 160px;
            }

            button:hover {
                background: #1d4ed8;
                transform: translateY(-1px);
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

            .fr-title {
                font-weight: 800;
                font-size: 16px;
            }

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

            .badge {
                display: inline-block;
                padding: 8px 14px;
                border-radius: 999px;
                font-size: 13px;
                font-weight: 800;
                border: 1px solid transparent;
            }

            .verstrichen {
                background: #fee2e2;
                color: #b91c1c;
                border-color: #fecaca;
            }

            .dringend {
                background: #ffedd5;
                color: #c2410c;
                border-color: #fed7aa;
            }

            .bald {
                background: #fef3c7;
                color: #b45309;
                border-color: #fde68a;
            }

            .ausstehend {
                background: #dcfce7;
                color: #15803d;
                border-color: #bbf7d0;
            }

            .erledigt {
                background: #dbeafe;
                color: #1d4ed8;
                border-color: #bfdbfe;
            }

            .tage {
                font-weight: 800;
                font-size: 16px;
            }

            .small {
                color: #6b7280;
                font-size: 13px;
                line-height: 1.5;
            }

            .actions {
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
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
            }

            .done-btn {
                color: #059669;
                background: #ecfdf5;
            }

            .done-btn:hover {
                border-color: #10b981;
                background: #d1fae5;
            }

            .delete-btn {
                color: #dc2626;
                background: #fef2f2;
            }

            .delete-btn:hover {
                border-color: #ef4444;
                background: #fee2e2;
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
                form {
                    grid-template-columns: 1fr 1fr;
                }

                button {
                    width: 100%;
                }
            }

            @media (max-width: 700px) {
                body {
                    padding: 18px;
                }

                .card {
                    padding: 18px;
                    border-radius: 18px;
                }

                form {
                    grid-template-columns: 1fr;
                }

                .topbar {
                    flex-direction: column;
                    align-items: stretch;
                }

                .stats {
                    width: 100%;
                }

                .stat-box {
                    flex: 1;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">

            <div class="topbar">
                <div class="title-wrap">
                    <h1>📅 Fristenkalender</h1>
                    <div class="subtitle">Modernisierte Übersicht nach Dringlichkeit, Zuständigkeit und Bearbeitungsstand</div>
                </div>

                <div class="stats">
                    <div class="stat-box">
                        <div class="stat-label">Gesamt</div>
                        <div class="stat-value">{{ fristen|length }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Offen</div>
                        <div class="stat-value">{{ fristen|selectattr('erledigt', 'equalto', False)|list|length }}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Erledigt</div>
                        <div class="stat-value">{{ fristen|selectattr('erledigt', 'equalto', True)|list|length }}</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Neue Frist anlegen</h2>
                <form method="post">
                    <div class="field">
                        <label>Frist / Vorgang</label>
                        <input type="text" name="name" placeholder="z. B. Klageerwiderung" required>
                    </div>

                    <div class="field">
                        <label>Aktenzeichen</label>
                        <input type="text" name="aktenzeichen" placeholder="z. B. 12 C 123/25" required>
                    </div>

                    <div class="field">
                        <label>Zuständig</label>
                        <input type="text" name="benutzer" placeholder="z. B. Fabi" required>
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
                            <th>Tage übrig</th>
                            <th>Status</th>
                            <th>Hinzugefügt</th>
                            <th>Aktion</th>
                        </tr>
                        {% for f in fristen %}
                        <tr class="{% if f.erledigt %}done-row{% endif %}">
                            <td><span class="fr-title">{{ f.name }}</span></td>
                            <td><span class="az">{{ f.aktenzeichen }}</span></td>
                            <td><span class="user-tag">{{ f.benutzer }}</span></td>
                            <td>{{ f.datum }}</td>
                            <td class="tage">{{ f.tage }}</td>
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
                            <td class="small">{{ f.hinzugefuegt }}</td>
                            <td>
                                <div class="actions">
                                    {% if not f.erledigt %}
                                        <a class="action-btn done-btn" href="/done/{{ loop.index0 }}">Erledigt</a>
                                    {% endif %}
                                    <a class="action-btn delete-btn" href="/delete/{{ loop.index0 }}" onclick="return confirm('Diesen Eintrag wirklich löschen?')">Löschen</a>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
                {% else %}
                    <div class="empty">
                        Noch keine Fristen vorhanden.
                    </div>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """

    return render_template_string(html, fristen=sortiert)


@app.route("/delete/<int:index>")
def delete(index):
    if 0 <= index < len(fristen):
        fristen.pop(index)
    return redirect("/")


@app.route("/done/<int:index>")
def done(index):
    if 0 <= index < len(fristen):
        fristen[index]["erledigt"] = True
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
