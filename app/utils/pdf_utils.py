import pdfplumber
import re
from typing import List, Dict, Tuple

def extract_questions_from_pdf(pdf_file) -> List[Dict]:
    """
    Extrait les questions d'un fichier PDF en cherchant les patterns comme 'Q1)', 'Q2)', etc.
    Retourne une liste de dictionnaires contenant les questions et leurs réponses.
    """
    questions = []
    with pdfplumber.open(pdf_file) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += "\n" + text

    # Découper sur les Qn)
    question_blocks = re.split(r'(Q\d+\))', full_text)
    for i in range(1, len(question_blocks), 2):
        q_number = question_blocks[i]
        q_content = question_blocks[i+1].strip() if i+1 < len(question_blocks) else ""
        if not q_content:
            continue
        lines = [l.strip() for l in q_content.split('\n') if l.strip()]
        # Les 4 dernières lignes = réponses, le reste = énoncé
        question_text = " ".join(lines[:-4])
        answers = lines[-4:]

        if len(lines) < 5:
            question_text = " ".join(lines)
            answers = []
        

        questions.append({
            'text': f'{q_number} {question_text}',
            'answers': [{'text': ans, 'is_correct': False} for ans in answers]
        })
    return questions

def extract_questions_from_text(text: str, delimiter: str = '\n') -> List[Dict]:
    """
    Extrait les questions d'un texte en utilisant un délimiteur spécifique.
    Pour chaque bloc, prend les 4 dernières lignes comme réponses, le reste comme énoncé.
    """
    questions = []
    # Découper sur les Qn)
    question_blocks = re.split(r'(Q\d+\))', text)
    for i in range(1, len(question_blocks), 2):
        q_number = question_blocks[i]
        q_content = question_blocks[i+1].strip() if i+1 < len(question_blocks) else ""
        if not q_content:
            continue
        lines = [l.strip() for l in q_content.split(delimiter) if l.strip()]
        if len(lines) < 5:
            continue
        question_text = " ".join(lines[:-4])
        answers = lines[-4:]
        questions.append({
            'text': f'{q_number} {question_text}',
            'answers': [{'text': ans, 'is_correct': False} for ans in answers]
        })
    return questions 