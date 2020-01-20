from flask import Flask, session, redirect, url_for, escape, request
from flask import render_template
import os


# Het spel draait om het ontsnappen. De speler gaat door verschillende ruimtes om uiteindelijk te ontsnappen (en
# proberen niet gepakt te worden). Die ruimtes kunnen we in één class definieren.
# Hieronder worden de objecten gestructureerd. Structuur in de zin van een naam, eigenschappen en
# methodes.


class Ruimte(object):
    # Met de init-functie worden de eigenschappen van de ruimtes gedefinieerd.
    # Verbindingen is een dictionary aangezien er meerder verbindingen kunnen zijn.
    def __init__(self, naam, beschrijving):
        self.naam = naam
        self.beschrijving = beschrijving
        self.verbindingen = {}

    # Deze functie kan voor elke ruimte de corresponderende verbindingen maken. Deze wordt gebruikt vanaf
    # regel 75 ongeveer.
    def voeg_toe(self, verbinding):
        self.verbindingen.update(verbinding)

    # Deze functie pakt de ruimte die is ingevoerd door de speler (door de 'POST' methode) uit de dictionary
    # verbindingen en geeft het als uitkomst.
    def ga_naar(self, richting):
        return self.verbindingen.get(richting)


# In de komende regels worden verschillende ruimtes gedefineerd.
# Daarbij worden de naam en beschrijving doorgegeven in de 'init-functie'.
cel = Ruimte('Cel',
             """
             Je bent onschuldig in een gevangenis beland. Je bent veroordeeld tot 5 jaar celstraf. 
             Er zit niets anders op dan je lot te aanvaarden. Totdat dat de bewaker langskomt en je een pakketje aanreikt. 
             Wat doe je? Als je het pakketje aannneemt is er een kans dat er iets leuks in zit of 
             dat het een flauwe grap is. Als je het pakketje niet aanneemt is er een kans dat de bewakers iets 
             vinden waardoor ze je kunnen betrappen.
             Kies: 'aannemen' of 'weigeren'.
             """
             )

tunnel = Ruimte('Tunnel',
                """
                Zodra de bewaker weg is maak je het pakketje snel open. Er zit een brief in! Daarop staat een datum en
                een code: 132. Dit moet wel van je handlanger zijn! De datum zal wel een mogelijke ontsnappingsdatum zijn.
                Naast de brief zit er ook een schepje in het pakketje. Je graaft urenlang een tunnel en stuit op een 
                harde muur. Je kunt verder naar links of naar rechts. Er is maar een beperkte tijd, dus kies wijs! 
                Kies: 'links' of 'rechts'
                """
                )

riool = Ruimte('Riool',
               """
               Je graaft door en komt in het riool terecht! Handel snel voordat de bewakers komen. Ai, daar is een
               hek. Er zit een cijferslot aan. Dan schiet opeens de code van de brief je te binnen. 
               Vul de drie-cijferige code in:
               """
               )

ontsnapt = Ruimte('Ontsnapt',
                  """
                  Het slot springt open. Je opent het hek, rent door het riool en klimt omhoog naar een putdeksel. 
                  Je kijkt om je heen en daar staat je handlanger te wachten in de auto. Je stapt in de auto.
                  Je bent ontsnapt!
                  """
                  )

betrapt = Ruimte('Betrapt',
                 """
                 Je bent betrapt! De bewaker duwt je terug de cel in.
                 """
                 )

# Hieronder zijn de verschillende verbindingen te vinden tussen de ruimtes. Deze worden via de functie voeg_toe()
# aan verbindingen toegevoegd per object.
riool.voeg_toe({
    '132': ontsnapt,
    '*': betrapt
})

tunnel.voeg_toe({
    'links': betrapt,
    'rechts': riool
})

cel.voeg_toe({
    'aannemen': tunnel,
    'weigeren': betrapt,
})


# Nadat een sessie is gestart en de value, gekoppeld aan de key ('ruimte_naam'), is opgeroepen,
# is het nodig om de juiste ruimte daarvan op te zoeken tussen alle objecten in dit bestand en
# die value daaraan gelijk te stellen. Deze functie wordt gebruikt in de functie spel().
def ruimte_oproepen(naam):
    return globals().get(naam)


# Met deze functie wordt de juiste naam van het object gevonden.
# Deze functie wordt gebruikt in de functie spel().
def vind_ruimte(naam):
    for key, value in globals().items():
        if value == naam:
            return key


app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)


# Als de pagina voor het eerst aangeroepen wordt met localhost:5000/, kan er een sessie worden gestart.
# 'ruimte_naam':'cel' is de key value relatie. Daarna verwijst de functie door naar de pagina '/spel'.
@app.route("/")
def index():
    session['ruimte_naam'] = 'cel'
    return redirect(url_for("spel"))


# Om het spel te spelen ('runnen'), worden de methodes 'POST' en 'GET' gebruikt. 'GET' om op basis
# van de huidige sessie de corresponderende html-file te laden. 'POST' om de input van de
# speler te gebruiken voor het bepalen van de volgende ruimte. Daarmee wordt de sessie up-to-date gemaakt.
@app.route("/spel", methods=['GET', 'POST'])
def spel():
    # Eerst wordt de naam opgevraagd van de ruimte uit de huidige sessie.
    ruimte_naam = session.get('ruimte_naam')
    # Als de aangevraagde methode 'GET' is, wordt de corresponderende html-bestand gezocht voor de huidige ruimte.
    # De huidige ruimte wordt gevonden door de functie ruimte_oproepen().
    if request.method == 'GET':
        ruimte = ruimte_oproepen(ruimte_naam)
        return render_template("browser.html", ruimte=ruimte)

    # Als de methode 'POST' is, wordt de input van de speler genomen via request.form. De volgende ruimte
    # wordt gezocht via de functie ga_naar(). Als deze bestaat in verbindingen (als eigenschap van deze ruimte),
    # dan wordt de sessie up-to-date gebracht met de functie vind_ruimte(). Als deze leeg is, dan wordt dezelfde
    # ruimte gebruikt.
    # Daarna wordt er doorverwezen naar de pagina '/spel' om met de nieuwe sessie de functie spel opnieuw te doorlopen.
    else:
        input_speler = request.form.get('input_speler')
        ruimte = ruimte_oproepen(ruimte_naam)
        volgende_ruimte = ruimte.ga_naar(input_speler)
        if volgende_ruimte:
            session['ruimte_naam'] = vind_ruimte(volgende_ruimte)
        else:
            session['ruimte_naam'] = vind_ruimte(ruimte)
        return redirect(url_for("spel"))


if __name__ == "__main__":
    app.run()
