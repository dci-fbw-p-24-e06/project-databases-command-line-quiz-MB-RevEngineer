import psycopg2
import random

# Datenbankverbindung herstellen
def connect_db():
    try:
        conn = psycopg2.connect(
            dbname="quizdb",
            user="dein_benutzername",
            password="dein_passwort",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print("Verbindungsfehler:", e)
        return None

# Holen Sie zufällig ausgewählte Fragen aus der entsprechenden Tabelle
def get_questions(topic, num_questions=5):
    conn = connect_db()
    if conn is None:
        return []
    cur = conn.cursor()
    try:
        # Hinweis: Das Tabellenname wird hier direkt verwendet. In einer produktiven Umgebung
        # sollten Sie Eingaben validieren, um SQL-Injection zu vermeiden.
        query = f"SELECT question, correct_answer, wrong1, wrong2, wrong3, wrong4, wrong5 FROM {topic} ORDER BY RANDOM() LIMIT {num_questions};"
        cur.execute(query)
        questions = cur.fetchall()
        return questions
    except Exception as e:
        print("Fehler beim Abrufen der Fragen:", e)
        return []
    finally:
        cur.close()
        conn.close()

# Quiz-Funktion: Fragt den Benutzer und wertet die Antworten aus
def quiz(topic):
    questions = get_questions(topic)
    if not questions:
        print("Keine Fragen gefunden oder Fehler beim Abrufen der Fragen.")
        return

    score = 0
    for idx, q in enumerate(questions, start=1):
        question_text = q[0]
        correct_answer = q[1]
        # Falsche Antworten können None sein, wenn weniger als 5 falsche Antworten vorhanden sind
        wrong_answers = [ans for ans in q[2:] if ans is not None]
        
        # Kombinieren und mischen der Antwortmöglichkeiten
        options = wrong_answers + [correct_answer]
        random.shuffle(options)
        
        print(f"\nFrage {idx}: {question_text}")
        for i, option in enumerate(options, start=1):
            print(f"{i}. {option}")
        
        try:
            user_choice = int(input("Deine Antwort (Zahl eingeben): "))
            if options[user_choice - 1] == correct_answer:
                print("Richtig!")
                score += 1
            else:
                print(f"Falsch. Die richtige Antwort wäre: {correct_answer}")
        except (ValueError, IndexError):
            print("Ungültige Eingabe, die Frage wird übersprungen.")
    
    print(f"\nQuiz beendet! Deine Punktzahl: {score} von {len(questions)}.")

# Funktion zum Hinzufügen einer neuen Frage
def add_question(topic):
    # Aufbau der neuen Frage
    question = input("Gib die Frage ein: ")
    correct_answer = input("Gib die korrekte Antwort ein: ")
    
    # Abfrage von mindestens zwei und maximal fünf falschen Antworten
    wrong_answers = []
    for i in range(1, 6):
        answer = input(f"Gib falsche Antwort {i} ein (oder drücke Enter, um zu beenden): ")
        if answer == "":
            break
        wrong_answers.append(answer)
    
    # Überprüfen, ob mindestens zwei falsche Antworten vorliegen
    if len(wrong_answers) < 2:
        print("Es müssen mindestens zwei falsche Antworten eingegeben werden.")
        return

    conn = connect_db()
    if conn is None:
        return
    cur = conn.cursor()
    
    try:
        # Prüfen, ob die Tabelle für das Thema existiert, wenn nicht, neu erstellen
        cur.execute(f"CREATE TABLE IF NOT EXISTS {topic} ("
                    "id SERIAL PRIMARY KEY, "
                    "module VARCHAR(50), "      # Optional: hier können Sie weitere Felder abfragen
                    "submodule VARCHAR(50), "
                    "difficulty INTEGER, "
                    "question TEXT, "
                    "correct_answer TEXT, "
                    "wrong1 TEXT, "
                    "wrong2 TEXT, "
                    "wrong3 TEXT, "
                    "wrong4 TEXT, "
                    "wrong5 TEXT"
                    ");")
        conn.commit()
        
        # Füllen der Spalten für falsche Antworten: Falls weniger als 5 falsche Antworten vorhanden sind, werden die restlichen Felder als NULL gesetzt.
        wrong_columns = wrong_answers + [None] * (5 - len(wrong_answers))
        insert_query = f"INSERT INTO {topic} (question, correct_answer, wrong1, wrong2, wrong3, wrong4, wrong5) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        cur.execute(insert_query, (question, correct_answer, *wrong_columns))
        conn.commit()
        print("Frage erfolgreich hinzugefügt!")
    except Exception as e:
        print("Fehler beim Hinzufügen der Frage:", e)
        conn.rollback()
    finally:
        cur.close()
        conn.close()

# Hauptmenü der Anwendung
def main():
    while True:
        print("\n--- Befehlszeilenquiz Menü ---")
        print("1. Quiz spielen")
        print("2. Frage hinzufügen")
        print("3. Beenden")
        
        choice = input("Wähle eine Option (1/2/3): ")
        if choice == "1":
            topic = input("Gib das Thema ein, zu dem du getestet werden möchtest: ")
            quiz(topic)
        elif choice == "2":
            topic = input("Gib das Thema ein, zu dem du eine Frage hinzufügen möchtest: ")
            add_question(topic)
        elif choice == "3":
            print("Programm wird beendet.")
            break
        else:
            print("Ungültige Eingabe. Bitte versuche es erneut.")

if __name__ == "__main__":
    main()