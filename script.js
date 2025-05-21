// Déclaration des questions
const questions = [
    {
        question: "En matière de régression linéaire, laquelle des alternatives suivantes ne comprend que des synonymes de ‘variable dépendante’ ?\n(i) Le régressant\n(ii) Le régresseur\n(iii) La variable expliquée\n(iv) La variable explicative\n(v) La variable de contrôle",
        answers:[
            {text: "(ii) et (iv) seulement.", correct: false},
            {text: "(i) et (iii) seulement.", correct: false},
            {text: "(i), (ii) et (iii) seulement.", correct: false},
            {text: "(i), (ii), (iii) et (v).", correct: true},
        ]
    },
    {
        question: "En matière de régression linéaire, laquelle des alternatives suivantes ne comprend que des synonymes de ‘variable indépendante’ ?\n(i) Le régresseur\n(ii) La variable de réponse\n(iii) La variable causale\n(iv) La variable d’effet",
        answers:[
            {text: "(ii) et (iv) seulement.", correct: true},
            {text: "(i) et (iii) seulement.", correct: false},
            {text: "(i), (ii) et (iii) seulement.", correct: false},
            {text: "(i), (ii), (iii) et (iv).", correct: false},
        ]
    },
    {
        question: "Laquelle des propositions suivantes est vraie concernant le modèle classique de régression?\ny a une distribution de probabilité.\nx a une distribution de probabilité.\nLe terme d’erreur peut être corrélé avec x.\nPour qu’un modèle soit adéquat, l’erreur estimée (e) doit être nulle pour chaque donnée observée.",
        answers:[
            {text: "y a une distribution de probabilité.", correct: false},
            {text: "x a une distribution de probabilité.", correct: false},
            {text: "Le terme d’erreur peut être corrélé avec x.", correct: true},
            {text: "Pour qu’un modèle soit adéquat, l’erreur estimée (e) doit être nulle pour chaque donnée observée.", correct: false},
        ]
    },
    {
        question: "Laquelle des propositions suivantes est vraie concernant l’estimation par MCO?\nMCO minimise la somme des distances verticales entre les données observées et la droite de régression.\nMCO minimise la somme des distances horizontales entres données observées et la droite de moyenne.\nMCO minimise la somme des carrés des distances verticales entre les données observées et la droite de moyenne.\nMCO minimise la somme des carrés des distances verticales entre les données observées et la droite de régression",
        answers:[
            {text: "MCO minimise la somme des distances verticales entre les données observées et la droite de régression.", correct: false},
            {text: "MCO minimise la somme des distances horizontales entres données observées et la droite de moyenne.", correct: false},
            {text: "MCO minimise la somme des carrés des distances verticales entre les données observées et la droite de moyenne.", correct: false},
            {text: "MCO minimise la somme des carrés des distances verticales entre les données observées et la droite de régression", correct: true},
        ]
    }
];

// Déclaration des éléments du DOM
const questionElement = document.getElementById("question");
const answerButtons = document.getElementById("answer-buttons");
const nextButton = document.getElementById("next-btn");

// Variables pour suivre l'état du quiz
let currentQuestionIndex = 0;
let score = 0;
let questionsDejaVues = new Set(); // Utiliser un ensemble pour stocker les indices des questions déjà vues

// Fonction pour démarrer le quiz
function startQuiz(){
    questionsDejaVues = new Set(); // Créer un nouvel ensemble vide à chaque démarrage du quiz
    currentQuestionIndex = Math.floor(Math.random() * questions.length);
    questionsDejaVues.add(currentQuestionIndex);
    score = 0;
    showQuestion();
}

// Fonction pour afficher la question actuelle
function showQuestion(){
    resetState();
    const currentQuestion = questions[currentQuestionIndex];
    questionElement.innerText = currentQuestion.question;

    // Clear previous answer buttons
    answerButtons.innerHTML = "";

    // Création des boutons de réponse pour la question actuelle
    currentQuestion.answers.forEach(answer => {
        const button = document.createElement("button");
        button.innerText = answer.text;
        button.classList.add("btn");
        answerButtons.appendChild(button);
        if (answer.correct){
            button.dataset.correct = answer.correct;
        }
        button.addEventListener("click", selectAnswer); 
    });
}

// Fonction pour réinitialiser l'état de l'interface utilisateur
function resetState(){
    nextButton.style.display = "none";
    nextButton.innerHTML = "Next"; // Remettre le texte du bouton à "Next"
    nextButton.removeEventListener("click", startQuiz); // Retirer l'écouteur d'événements "startQuiz"
    nextButton.removeEventListener("click", handleNextButton); // Retirer l'écouteur d'événements "handleNextButton"
    nextButton.addEventListener("click", handleNextButton); // Ajouter l'écouteur d'événements "handleNextButton"
    while(answerButtons.firstChild){
        answerButtons.removeChild(answerButtons.firstChild);
    }
}

// Fonction pour sélectionner une réponse à une question
function selectAnswer(e){
    const selectedBtn = e.target;
    const isCorrect = selectedBtn.dataset.correct === "true";
    if (isCorrect){
        selectedBtn.classList.add("correct");
        score++;
    } else {
        selectedBtn.classList.add("incorrect");
        // Trouver et afficher la réponse correcte
        Array.from(answerButtons.children).forEach(button => {
            if (button.dataset.correct === "true") {
                button.classList.add("correct");
            }
        });
    }
    // Désactiver tous les boutons de réponse après avoir choisi une réponse
    Array.from(answerButtons.children).forEach(button => {
        button.disabled = true;
    });
    nextButton.style.display = "block";
}


// Fonction pour afficher le score à la fin du quiz
function showScore(){
    resetState();
    questionElement.innerHTML = `Vous avez obtenu ${score} sur ${questions.length} points`;
    nextButton.innerHTML = "Rejouer"; // Modifier le texte du bouton en "Rejouer"
    nextButton.removeEventListener("click", handleNextButton); // Retirer l'écouteur d'événements "handleNextButton"
    nextButton.addEventListener("click", startQuiz); // Ajouter l'écouteur d'événements "startQuiz"
    nextButton.style.display = "block";
}

// Fonction pour gérer le bouton "Suivant"
function handleNextButton(){
    if(questionsDejaVues.size < questions.length){ // Vérifiez si vous avez déjà vu toutes les questions
        let newIndex;
        do {
            newIndex = Math.floor(Math.random() * questions.length);
        } while (questionsDejaVues.has(newIndex)); // Vérifiez si l'indice généré est déjà dans questionsDejaVues
        questionsDejaVues.add(newIndex);
        currentQuestionIndex = newIndex;
        showQuestion();
    } else {
        showScore();
    }
}

// Démarrer le quiz au chargement de la page
startQuiz();
