document.getElementById("analyze-btn").addEventListener("click", function() {
    const inputText = document.getElementById("quiz-text").value;
    const questionsAndAnswers = splitQuestions(inputText);
    const questions = questionsAndAnswers.map(parseQuestionsAndAnswers);

    // Demander à l'utilisateur de fournir le numéro de la bonne réponse
    questions.forEach((question, index) => {
        console.log(question.question);
        question.answers.forEach((answer, j) => {
            console.log(`${j + 1}. ${answer.text}`);
        });

        let user_input;
        do {
            user_input = parseInt(prompt("Entrez le numéro de la bonne réponse pour la question " + (index + 1) + " :"));
        } while (isNaN(user_input) || user_input < 1 || user_input > question.answers.length);

        question.answers[user_input - 1].correct = true;
    });

    // Écrire les questions dans un fichier JSON
    try {
        fs.writeFileSync("questions.json", JSON.stringify(questions, null, 4));
        displayAnalysisResults(questions);
    } catch (error) {
        console.error("Erreur lors de l'écriture dans le fichier JSON :", error);
    }
});

// Fonction pour découper toutes les questions
function splitQuestions(input_text) {
    const question_pattern = /(Q\d+\))([\s\S]*?)(?=(Q\d+\)|$))/g;
    const questions_and_answers = [...input_text.matchAll(question_pattern)];
    return questions_and_answers.map(match => match.slice(1).join('').trim());
}

// Fonction pour découper les questions et les réponses
function parseQuestionsAndAnswers(input_text) {
    const lines = input_text.split('\n');
    let currentQuestion = '';
    let currentAnswers = [];

    // Extraire les réponses jusqu'à en avoir quatre
    while (currentAnswers.length < 4 && lines.length > 0) {
        const line = lines.shift().trim();
        if (line !== '') {
            currentAnswers.push(line);
        }
    }

    // Si nous avons encore des lignes après l'extraction des réponses, elles font partie de la question
    if (lines.length > 0) {
        currentQuestion = lines.join('\n').trim();
    }

    // Convertir les réponses en objets avec les bonnes clés
    const formattedAnswers = currentAnswers.map(answer => ({ text: answer, correct: false }));
    return { question: currentQuestion, answers: formattedAnswers };
}

function displayAnalysisResults(quizData) {
    const analysisResultsDiv = document.getElementById("analysis-results");
    analysisResultsDiv.innerHTML = "";

    quizData.forEach((questionData, index) => {
        const questionDiv = document.createElement("div");
        questionDiv.innerHTML = `<h3>Question ${index + 1}:</h3><p>${questionData.question}</p>`;
        const answersUl = document.createElement("ul");
        questionData.answers.forEach((answer, i) => {
            const answerLi = document.createElement("li");
            answerLi.textContent = answer.text; // Afficher le texte de la réponse
            answersUl.appendChild(answerLi);
        });
        questionDiv.appendChild(answersUl);
        analysisResultsDiv.appendChild(questionDiv);
    });
}
