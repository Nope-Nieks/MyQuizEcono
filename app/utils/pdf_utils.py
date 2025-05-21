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
        if q_content:
            # Découper en lignes
            lines = [l.strip() for l in q_content.split('\n') if l.strip()]
            if not lines:
                continue
            # On prend la première ligne comme énoncé, le reste comme réponses
            question_text = lines[0]
            answers = lines[1:]  # Peut être vide si pas de réponses détectées
            questions.append({
                'text': f"{q_number} {question_text}",
                'answers': [{'text': ans, 'is_correct': False} for ans in answers]
            })
    return questions

def extract_questions_from_text(text: str, delimiter: str = '\n') -> List[Dict]:
    """
    Extrait les questions d'un texte en utilisant un délimiteur spécifique.
    """
    questions = []
    current_question = None
    current_answers = []
    
    lines = text.split(delimiter)
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Chercher le pattern de question (Q1), Q2), etc.)
        question_match = re.match(r'Q(\d+)\)\s*(.*)', line)
        
        if question_match:
            # Si on a une question en cours, on la sauvegarde
            if current_question:
                questions.append({
                    'text': current_question,
                    'answers': current_answers
                })
            
            # Commencer une nouvelle question
            current_question = question_match.group(2)
            current_answers = []
        else:
            # Chercher les réponses (A), B), C), D))
            answer_match = re.match(r'([A-D])\)\s*(.*)', line)
            if answer_match and current_question:
                current_answers.append({
                    'text': answer_match.group(2),
                    'is_correct': False  # À déterminer plus tard
                })
    
    # Ajouter la dernière question
    if current_question:
        questions.append({
            'text': current_question,
            'answers': current_answers
        })
    
    return questions 