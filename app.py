from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = 'geheimes-passwort'  # سر الجلسة

# كلمة سر الدخول للوحة المشرف
ADMIN_PASSWORD = "1234"

# الصفحة الرئيسية
@app.route("/")
def home():
    return render_template("home.html")

# صفحة تقديم الطلب
@app.route("/bestellen", methods=["GET", "POST"])
def bestellen():
    if request.method == "POST":
        name = request.form["name"]
        adresse = request.form["adresse"]
        whatsapp = request.form["whatsapp"]
        liste = request.form["liste"]
        markt = request.form["markt"]

        with open("bestellungen.txt", "a", encoding="utf-8") as f:
            f.write(f"Name: {name}\nAdresse: {adresse}\nWhatsApp: {whatsapp}\nSupermarkt: {markt}\nListe:\n{liste}\n{'-'*40}\n")

        return redirect("/")
    return render_template("bestellen.html")

# صفحة تسجيل الدخول للمشرف
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pw = request.form["password"]
        if pw == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin")
        else:
            return "Falsches Passwort"
    return render_template("login.html")

# صفحة عرض الطلبات (لوحة المشرف)
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")

    try:
        with open("bestellungen.txt", "r", encoding="utf-8") as f:
            blocks = f.read().split('----------------------------------------')
    except FileNotFoundError:
        blocks = []

    anfragen = []
    for i, block in enumerate(blocks):
        lines = block.strip().splitlines()
        if lines:
            count = 1
            new_block = []
            whatsapp = ""
            for line in lines:
                if line.startswith("Liste:"):
                    new_block.append("Liste:")
                elif line.strip() and not any(x in line for x in ["Name:", "Adresse:", "WhatsApp:", "Supermarkt", "Liste:"]):
                    new_block.append(f"{count}. {line}")
                    count += 1
                else:
                    new_block.append(line)
                if line.startswith("WhatsApp:"):
                    whatsapp = line.replace("WhatsApp:", "").strip()
            anfragen.append({"id": i, "text": "\n".join(new_block), "whatsapp": whatsapp})

    return render_template("admin.html", anfragen=anfragen)

# حذف الطلب (تم التوصيل)
@app.route("/delete/<int:id>")
def delete(id):
    if not session.get("admin"):
        return redirect("/login")

    try:
        with open("bestellungen.txt", "r", encoding="utf-8") as f:
            blocks = f.read().split('----------------------------------------')
    except FileNotFoundError:
        blocks = []

    if 0 <= id < len(blocks):
        del blocks[id]
        with open("bestellungen.txt", "w", encoding="utf-8") as f:
            for b in blocks:
                if b.strip():
                    f.write(b.strip() + "\n" + "-"*40 + "\n")

    return redirect("/admin")

# تسجيل الخروج
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
