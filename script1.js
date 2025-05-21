document.addEventListener("DOMContentLoaded", function() {
    const questionElement = document.getElementById("question");
    const answerButtons = document.getElementById("answer-buttons");
    const nextButton = document.getElementById("next-btn");
    const homeButton = document.getElementById("home-btn"); // Sélectionnez le bouton "Home"

    // Fonction pour rediriger vers la page d'accueil
    function goToHomePage() {
        window.location.href = "acceuil.html"; // Remplacez "index.html" par le nom de votre page d'accueil
    }

    // Ajoutez un écouteur d'événements au bouton "Home" pour déclencher la redirection
    homeButton.addEventListener("click", goToHomePage);

    // Variables pour suivre l'état du quiz
    let currentQuestionIndex = 0;
    let score = 0;
    let questionsDejaVues = new Set();; // Tableau pour stocker les questions

    // Fonction pour démarrer le quiz
    function startQuiz(){
        fetch('questions.json') // Charger les questions à partir du fichier JSON
        .then(response => response.json())
        .then(data => {
            questionsDejaVues =  new Set();
            questions = data; // Stocker les questions dans la variable questions
            currentQuestionIndex = Math.floor(Math.random() * questions.length);
            questionsDejaVues.add(currentQuestionIndex);
            score = 0;
            showQuestion();
        })
        .catch(error => {
            console.error('Erreur lors du chargement des questions:', error);
        });
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
});



