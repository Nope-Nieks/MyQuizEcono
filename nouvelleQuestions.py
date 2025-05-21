import re
import json

# fonction pour découper toutes les questions
def splitQuestions(input_text):
    question_pattern = r"(Q\d+\))([\s\S]*?)(?=(Q\d+\)|$))"
    questions_and_answers = re.findall(question_pattern, input_text)
    return questions_and_answers

# Fonction pour découper les questions et les réponses
def parse_questions_and_answers(input_text):
    lines = input_text.split("\n")
    current_question = ""
    current_answers = []
    lines = lines[::-1]
    
    # Extraire les réponses jusqu'à en avoir quatre
    while len(current_answers) < 4 and lines:
        line = lines.pop(0)
        if line.strip():  # Ignorer les lignes vides
            current_answers.append(line.strip())
    current_answers = current_answers[::-1]
    lines = lines[::-1]
    # Si nous avons encore des lignes après l'extraction des réponses, elles font partie de la question
    if lines:
        current_question = "\n".join(lines)

    # Convertir les réponses en objets avec les bonnes clés
    formatted_answers = [{"text": answer, "correct": False} for answer in current_answers]
    return {"question": current_question, "answers": formatted_answers}

# Texte contenant les questions et les réponses
input_text = """
Q1) En matière de régression linéaire, laquelle des alternatives suivantes ne comprend que des
synonymes de ‘variable dépendante’ ?
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
synonymes de ‘variable indépendante’ ?
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

questions_and_answers = splitQuestions(input_text)

questions = []
for question_text in questions_and_answers:
    questions.append(parse_questions_and_answers(question_text[1]))

# Demander à l'utilisateur de fournir le numéro de la bonne réponse
for i, question in enumerate(questions, 1):
    print(question['question'])
    for j, answer in enumerate(question['answers'], 1):
        print(f"{j}. {answer['text']}")
    user_input = int(input("Entrez le numéro de la bonne réponse : "))
    question['answers'][user_input - 1]['correct'] = True

# Écrire les questions dans un fichier JSON
with open("questions.json", "w") as file:
    json.dump(questions, file, indent=4)
