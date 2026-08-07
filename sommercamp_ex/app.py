# Hier importieren wir die benötigten Softwarebibliotheken.
from os.path import abspath, exists
from sys import argv
import streamlit as st
from streamlit import (text_input, header, title, subheader, container,
                       markdown, link_button, divider, set_page_config)
from pyterrier import IndexFactory
from pyterrier.terrier import Retriever
from pyterrier.text import get_text

import pyterrier
import pyterrier_dr

import json
from streamlit_lottie import st_lottie

# Diese Funktion baut die App für die Suche im gegebenen Index auf.
def app(index_dir) -> None:

    # Konfiguriere den Titel der Web-App (wird im Browser-Tab angezeigt)
    set_page_config(
        page_title="Sim Racing-Suchmaschine",
        layout="centered",
    )

    # Gib der App einen Titel und eine Kurzbeschreibung:
    title("Racing-Suchmaschine")
    markdown("Hier kannst du unsere neue Racing-Suchmaschine nutzen:")

    # Erstelle ein Text-Feld, mit dem die Suchanfrage (query)
    # eingegeben werden kann.
    query = text_input(
        label="Suchanfrage",
        placeholder="Suche...",
        value="",
    )

    def load_lottie(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    lottie_ai = load_lottie("data/animations/ai animation Flow 1.json")

    with st.container():
        on = st.toggle("Activate AI-Mode")
        if on:
            st.write("AI-Mode aktiviert")
            st_lottie(
                lottie_ai,
                speed=1,
                loop=True,
                height=200,
                key="ai_mode"
            )
            action = st.menu_button("Ai-Model", options=["Lite 6.4", "Pro 12.8"])

    # Wenn die Suchanfrage leer ist, dann kannst du nichts suchen.
    if query == "":
        markdown("Bitte gib eine Suchanfrage ein.")
        return
    elif on:
        # Öffne den Index.
        index = IndexFactory.of(abspath(index_dir))
        # Initialisiere den Such-Algorithmus
        searcher = Retriever(
            index,
            wmodel="BM25",
            num_results=128,
        )

        if action == "Lite 6.4":
            # Initialisiere das Modul, zum Abrufen der Texte.
            text_getter = get_text(index, metadata=["url", "title", "text"])
            # Dense retriver Model laden
            model = pyterrier_dr.SBertBiEncoder('sentence-transformers/all-MiniLM-L6-v2')
            pipeline = searcher >> text_getter
            pipeline = (pipeline % 5 >> model.scorer()) ^ pipeline

            # Führe die Such-Pipeline aus und suche nach der Suchanfrage.
            results = pipeline.search(query)

            # Zeige eine Unter-Überschrift vor den Suchergebnissen an.
            divider()
            header("Suchergebnisse")

            # Wenn die Ergebnisliste leer ist, gib einen Hinweis aus.
            if len(results) == 0:
                markdown("Keine Suchergebnisse.")
                return

            # Wenn es Suchergebnisse gibt, dann zeige an, wie viele.
            markdown(f"{len(results)} Suchergebnisse.")

            # Gib nun der Reihe nach, alle Suchergebnisse aus.
            for _, row in results.iterrows():
                # Pro Suchergebnis, erstelle eine Box (container).
                with container(border=True):
                    # Zeige den Titel der gefundenen Webseite an.
                    subheader(row["title"])
                    # Speichere den Text in einer Variablen (text).
                    text = row["text"]
                    # Schneide den Text nach 500 Zeichen ab.
                    text = text[:500]
                    # Ersetze Zeilenumbrüche durch Leerzeichen.
                    text = text.replace("\n", " ")
                    # Zeige den Dokument-Text an.
                    markdown(text)
                    # Gib Nutzern eine Schaltfläche, um die Seite zu öffnen.
                    link_button("Seite öffnen", url=row["url"])

        elif action == "Pro 12.8":
            # Initialisiere das Modul, zum Abrufen der Texte.
            text_getter = get_text(index, metadata=["url", "title", "text"])
            # Dense retriver Model laden
            model = pyterrier_dr.SBertBiEncoder('sentence-transformers/all-MiniLM-L6-v2')
            pipeline = searcher >> text_getter >> model.scorer()

            # Führe die Such-Pipeline aus und suche nach der Suchanfrage.
            results = pipeline.search(query)

            # Zeige eine Unter-Überschrift vor den Suchergebnissen an.
            divider()
            header("Suchergebnisse")

            # Wenn die Ergebnisliste leer ist, gib einen Hinweis aus.
            if len(results) == 0:
                markdown("Keine Suchergebnisse.")
                return

            # Wenn es Suchergebnisse gibt, dann zeige an, wie viele.
            markdown(f"{len(results)} Suchergebnisse.")

            # Gib nun der Reihe nach, alle Suchergebnisse aus.
            for _, row in results.iterrows():
                # Pro Suchergebnis, erstelle eine Box (container).
                with container(border=True):
                    # Zeige den Titel der gefundenen Webseite an.
                    subheader(row["title"])
                    # Speichere den Text in einer Variablen (text).
                    text = row["text"]
                    # Schneide den Text nach 500 Zeichen ab.
                    text = text[:500]
                    # Ersetze Zeilenumbrüche durch Leerzeichen.
                    text = text.replace("\n", " ")
                    # Zeige den Dokument-Text an.
                    markdown(text)
                    # Gib Nutzern eine Schaltfläche, um die Seite zu öffnen.
                    link_button("Seite öffnen", url=row["url"])

    elif on is False:

        # Öffne den Index.
        index = IndexFactory.of(abspath(index_dir))
        # Initialisiere den Such-Algorithmus.
        searcher = Retriever(
            index,
            wmodel="BM25",
            num_results=10,
        )
        # Initialisiere das Modul, zum Abrufen der Texte.
        text_getter = get_text(index, metadata=["url", "title", "text"])
        # Baue die Such-Pipeline zusammen.
        pipeline = searcher >> text_getter
        # Führe die Such-Pipeline aus und suche nach der Suchanfrage.
        results = pipeline.search(query)

        # Zeige eine Unter-Überschrift vor den Suchergebnissen an.
        divider()
        header("Suchergebnisse")

        # Wenn die Ergebnisliste leer ist, gib einen Hinweis aus.
        if len(results) == 0:
            markdown("Keine Suchergebnisse.")
            return

        # Wenn es Suchergebnisse gibt, dann zeige an, wie viele.
        markdown(f"{len(results)} Suchergebnisse.")

        # Gib nun der Reihe nach, alle Suchergebnisse aus.
        for _, row in results.iterrows():
            # Pro Suchergebnis, erstelle eine Box (container).
            with container(border=True):
                # Zeige den Titel der gefundenen Webseite an.
                subheader(row["title"])
                # Speichere den Text in einer Variablen (text).
                text = row["text"]
                # Schneide den Text nach 500 Zeichen ab.
                text = text[:500]
                # Ersetze Zeilenumbrüche durch Leerzeichen.
                text = text.replace("\n", " ")
                # Zeige den Dokument-Text an.
                markdown(text)
                # Gib Nutzern eine Schaltfläche, um die Seite zu öffnen.
                link_button("Seite öffnen", url=row["url"])


# Die Hauptfunktion, die beim Ausführen der Datei aufgerufen wird.
def main():
    # Lade den Pfad zum Index aus dem ersten Kommandozeilen-Argument.
    index_dir = argv[1]

    # Wenn es noch keinen Index gibt, kannst du die Suchmaschine nicht starten.
    if not exists(index_dir):
        exit(1)

    # Rufe die App-Funktion von oben auf.
    app(index_dir)


if __name__ == "__main__":
    main()