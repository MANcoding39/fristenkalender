from flask import Flask, request, redirect, render_template_string
from datetime import datetime

app = Flask(__name__)

fristen = []


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        datum = request.form["datum"]
        hinzugefuegt = datetime.now().strftime("%d.%m.%Y %H:%M")

        fristen.append({
            "name": name,
            "datum": datum,
            "hinzugefuegt": hinzugefuegt
        })
        return redirect("/")

    heute = datetime.today()

    for f in fristen:
        f["datum_obj"] = datetime.strptime(f["datum"], "%Y-%m-%d")
        f["tage"] = (f["datum_obj"] - heute).days

    sortiert = sorted(fristen, key=lambda x: x["tage"])

    html = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <title>Manouchehri Fristenkalender</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
                padding: 30px;
                color: #222;
            }

            .container {
                max-width: 1100px;
                margin: auto;
                background: white;
                padding: 30px;
                border-radius: 16px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.08);
            }

            h1 {
                margin-top: 0;
                margin-bottom: 25px;
                font-size: 30px;
                color: #1f2937;
            }

            .subtitle {
                color: #6b7280;
                margin-bottom: 25px;
            }

            form {
                display: flex;
                gap: 12px;
                flex-wrap: wrap;
                margin-bottom: 30px;
            }

            input, button {
                padding: 12px 14px;
                font-size: 15px;
                border-radius: 10px;
                border: 1px solid #d1d5db;
            }

            input {
                background: #fff;
            }

            button {
                background: #2563eb;
                color: white;
                border: none;
                cursor: pointer;
                font-weight: bold;
                transition: 0.2s;
            }

            button:hover {
                background: #1d4ed8;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                overflow: hidden;
                border-radius: 12px;
            }

            th {
                background: #f3f4f6;
                color: #374151;
                text-align: left;
                padding: 14px;
                font-size: 14px;
            }

            td {
                padding: 14px;
                border-top: 1px solid #e5e7eb;
                vertical-align: middle;
            }

            tr:hover {
                background: #f9fafb;
            }

            .badge {
                display: inline-block;
                padding: 6px 12px;
                border-radius: 999px;
                font-size: 13px;
                font-weight: bold;
            }

            .verstrichen {
                background: #fee2e2;
                color: #b91c1c;
            }

            .dringend {
                background: #ffedd5;
                color: #c2410c;
            }

            .bald {
                background: #fef3c7;
                color: #b45309;
            }

            .ausstehend {
                background: #dcfce7;
                color: #15803d;
            }

            .delete-btn {
                color: #dc2626;
                text-decoration: none;
                font-weight: bold;
            }

            .delete-btn:hover {
                text-decoration: underline;
            }

            .small {
                color: #6b7280;
                font-size: 13px;
            }

            .tage {
                font-weight: bold;
            }
            .empty {
                padding: 25px;
                text-align: center;
                color: #6b7280;
                background: #f9fafb;
                border-radius: 12px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📅 Fristenkalender</h1>
            <div class="subtitle">Übersicht aller offenen Fristen nach Dringlichkeit sortiert</div>

            <form method="post">
                <input type="text" name="name" placeholder="Frist / Vorgang" required>
                <input type="date" name="datum" required>
                <button type="submit">+ Hinzufügen</button>
            </form>

            {% if fristen %}
            <table>
                <tr>
                    <th>Frist</th>
                    <th>Fällig am</th>
                    <th>Tage übrig</th>
                    <th>Status</th>
                    <th>Hinzugefügt am</th>
                    <th>Aktion</th>
                </tr>
                {% for f in fristen %}
                <tr>
                    <td><strong>{{ f.name }}</strong></td>
                    <td>{{ f.datum }}</td>
                    <td class="tage">{{ f.tage }}</td>
                    <td>
                        {% if f.tage < 0 %}
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
                        <a class="delete-btn" href="/delete/{{ loop.index0 }}" onclick="return confirm('Diesen Eintrag wirklich löschen?')">Löschen</a>
                    </td>
                </tr>
                {% endfor %}
            </table>
            {% else %}
                <div class="empty">
                    Noch keine Fristen vorhanden.
                </div>
            {% endif %}
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


if __name__ == "__main__":
    app.run(debug=True)