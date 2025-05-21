from flask import Flask, render_template, request, jsonify
import json
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/parse', methods=['POST'])
def parse():
    input_text = request.form['input_text']
    questions_and_answers = split_questions(input_text)
    questions = [parse_question_and_answers(question_text[1]) for question_text in questions_and_answers]
    return jsonify(questions)

def split_questions(input_text):
    """Split the input text into individual questions"""
    question_pattern = r"(Q\d+\))([\s\S]*?)(?=(Q\d+\)|$))"
    return re.findall(question_pattern, input_text)

def parse_question_and_answers(question_text):
    """Parse a single question and its answers"""
    lines = question_text.split("\n")
    lines = lines[::-1]
    answers = extract_answers(lines)
    question = "\n".join(lines[::-1])
    return {"question": question, "answers": format_answers(answers)}


def split_questions(input_text):
    """Split the input text into individual questions"""
    question_pattern = r"(Q\d+\))([\s\S]*?)(?=(Q\d+\)|$))"
    return re.findall(question_pattern, input_text)

def extract_answers(lines):
    """Extract up to 4 answers from the lines"""
    answers = []
    while len(answers) < 4 and lines:
        line = lines.pop(0)
        if line.strip():  # Ignore empty lines
            answers.append(line.strip())
    return answers[::-1]

def format_answers(answers):
    """Format the answers into a list of dictionaries"""
    return [{"text": answer, "correct": False} for answer in answers]

def parse_question_and_answers(question_text):
    """Parse a single question and its answers"""
    lines = question_text.split("\n")
    lines = lines[::-1]
    answers = extract_answers(lines)
    question = "\n".join(lines[::-1])
    return {"question": question, "answers": format_answers(answers)}

def ask_user_for_answer(question):
    """Ask the user to select the correct answer"""
    for i, answer in enumerate(question["answers"], 1):
        print(f"{i}. {answer['text']}")
    while True:
        try:
            user_input = int(input("Enter the number of the correct answer: "))
            if 1 <= user_input <= len(question["answers"]):
                question["answers"][user_input - 1]["correct"] = True
                break
            else:
                print("Invalid input. Please try again.")
        except ValueError:
            print("Invalid input. Please try again.")

def write_questions_to_json(questions, filename):
    """Write the questions to a JSON file"""
    with open(filename, "w") as file:
        json.dump(questions, file, indent=4)

input_text = """
Q1) En matière de régression linéaire, laquelle des alternatives suivantes ne comprend que des
synonymes de ‘variable dépendante’?
(i) Le régressant
(ii) Le régresseur
(iii) La variable expliquée
(iv) La variable explicative
(v) La variable de contrôle 
(ii) et (iv) seulement.
(i) et (iii) seulement.
(i), (ii) et (iii) seulement.
(i), (ii), (iii) et (v).

Q2) En matière de régression linéaire, laquelle des alternatives suivantes ne comprend que des
synonymes de ‘variable indépendante’?
(i) Le régresseur
(ii) La variable de réponse=
(iii) La variable causale
(iv) La variable d’effet
(ii) et (iv) seulement.
(i) et (iii) seulement.
(i), (ii) et (iii) seulement.
(i), (ii), (iii) et (iv).

Q3) Laquelle des propositions suivantes est vraie concernant le modèle classique de régression?
y a une distribution de probabilité.
x a une distribution de probabilité.
Le terme d’erreur peut être corrélé avec x.
Pour qu’un modèle soit adéquat, l’erreur estimée (e) doit être nulle pour chaque donnée observée.
Q4) Laquelle des propositions suivantes est vraie concernant l’estimation par MCO?
MCO minimise la somme des distances verticales entre les données observées et la droite de
régression.
MCO minimise la somme des distances horizontales entres données observées et la droite de
moyenne.
MCO minimise la somme des carrés des distances verticales entre les données observées et la
droite de moyenne.
MCO minimise la somme des carrés des distances verticales entre les données observées et la
droite de régression.
"""

questions_and_answers = split_questions(input_text)
questions = [parse_question_and_answers(question_text[1]) for question_text in questions_and_answers]

for i, question in enumerate(questions, 1):
    print(question["question"])
    ask_user_for_answer

if __name__ == '__main__':
    app.run(debug=True)