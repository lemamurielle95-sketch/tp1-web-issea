
from flask import Flask, jsonify, request, send_from_directory
from pathlib import Path
import csv
import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

app = Flask(__name__)
DOSSIER = Path(__file__).resolve().parent


# Page d'accueil
@app.route("/")
def accueil():
    return send_from_directory(DOSSIER, "releve.html")


# Fichier CSS
@app.route("/style.css")
def style():
    return send_from_directory(DOSSIER, "style.css")


# Route bonjour
@app.route("/bonjour/<ville>")
def bonjour(ville):
    return (
        f"<h1>Bonjour {ville} !</h1>"
        "<p>Bienvenue sur notre serveur Python.</p>"
    )


# API des prix
@app.route("/api/prix")
def api_prix():
    fichier = DOSSIER / "prix.csv"

    with open(fichier, "r", encoding="utf-8-sig",
              newline="") as f:
        prix = list(csv.DictReader(f))

    ville = request.args.get("ville")
    produit = request.args.get("produit")

    if ville:
        prix = [
            ligne for ligne in prix
            if ligne["ville"].lower() == ville.lower()
        ]

    if produit:
        prix = [
            ligne for ligne in prix
            if ligne["produit"].lower() == produit.lower()
        ]

    for ligne in prix:
        ligne["prix"] = float(ligne["prix"])

    return jsonify({
        "nombre": len(prix),
        "prix": prix
    })


# Bonus : population du Cameroun
@app.route("/population")
def population():
    url = (
        "https://api.worldbank.org/v2/country/CMR/"
        "indicator/SP.POP.TOTL?format=json"
    )

    try:
        with urlopen(url, timeout=10) as reponse:
            donnees = json.loads(
                reponse.read().decode("utf-8")
            )

        observations = donnees[1] if len(donnees) > 1 else []

        derniere = next(
            (x for x in observations
             if x.get("value") is not None),
            None
        )

        if derniere is None:
            return "Population indisponible.", 502

        annee = derniere["date"]
        habitants = int(derniere["value"])

        return (
            "<h1>Population du Cameroun</h1>"
            f"<p>Année : {annee}</p>"
            f"<p>Population : {habitants:,} habitants</p>"
        )

    except (URLError, HTTPError, TimeoutError,
            ValueError, IndexError):
        return (
            "Impossible de récupérer les données de la "
            "Banque mondiale. Vérifiez votre connexion.",
            502
        )


if __name__ == "__main__":
    app.run(debug=True)
