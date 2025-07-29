let questions = [];
let currentQuestion = 0;
let score = 0;
let selectedLang = "de";
let selectedLevel = "curious";
let wrongAnswers = [];
let maxQuestionsPerQuiz  = 5; //goal 21

function setupQuizControls() {
  document.getElementById("language").addEventListener("change", (e) => selectedLang = e.target.value);
  document.getElementById("level").addEventListener("change", (e) => selectedLevel = e.target.value);
  document.getElementById("startButton").addEventListener("click", startQuiz);
}


async function loadQuestions() {
    const res = await fetch(`lang/${selectedLang}.json`);
    const data = await res.json();
    const filtered = data.filter(q => q.difficulty.includes(selectedLevel));
    let extended = [...filtered];
    while (extended.length < maxQuestionsPerQuiz) {
        extended.push(...shuffle(filtered));
    }
    return shuffle(extended).slice(0, maxQuestionsPerQuiz);
}

function shuffle(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
}

async function startQuiz() {
    questions = await loadQuestions();
    currentQuestion = 0;
    score = 0;
    wrongAnswers = [];
    showQuestion();
}

function showQuestion() {
    const q = questions[currentQuestion];
    const container = document.getElementById("quiz");
    container.innerHTML = `<p><b>${currentQuestion + 1}/${maxQuestionsPerQuiz}:</b> ${q.question}</p>` +
        q.options.map((opt, i) =>
            `<button onclick="checkAnswer(${i})">${opt}</button>`
        ).join("<br>");
}

function checkAnswer(answerIndex) {
    const question = questions[currentQuestion];
    const isCorrect = question.answer === answerIndex;

    if (isCorrect) {
        score++;
    } else {
        wrongAnswers.push({
            question: question.question,
            correctAnswer: question.options[question.answer],
            yourAnswer: question.options[answerIndex]
        });
    }

    currentQuestion++;

    if (currentQuestion < questions.length) {
        showQuestion();
    } else {
        showResults();
    }
}

function showResults() {
    let level;
    const percentage = score / questions.length;
    
    if (percentage >= 0.85) level = "🟢 Satoshi-Level!";
    else if (percentage >= 0.6) level = "🟡 Bitcoiner-Level";
    else level = "🔴 Curious-Level";

    let resultHTML = `<h2>Score: ${score}/${questions.length}</h2>`;
    resultHTML += `<p>${level}</p>`;

    if (wrongAnswers.length > 0) {
        resultHTML += "<h3>Falsche Antworten:</h3><ul>";
        wrongAnswers.forEach((item, index) => {
            resultHTML += `
                <li>
                    <strong>Frage ${index + 1}:</strong> ${item.question}<br>
                    <strong>Deine Antwort:</strong> ${item.yourAnswer}<br>
                    <strong>Richtige Antwort:</strong> ${item.correctAnswer}
                </li><br>
            `;
        });
        resultHTML += "</ul>";
    } else {
        resultHTML += "<p>Perfekt! 🎉 Du hast alles richtig beantwortet.</p>";
    }

    document.getElementById("quiz").innerHTML = resultHTML;
}

window.setupQuizControls = setupQuizControls;
