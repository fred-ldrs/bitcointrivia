let questions = [];
let currentQuestion = 0;
let score = 0;
let selectedLang = "de";
let selectedLevel = "curious";
let wrongAnswers = [];
let maxQuestionsPerQuiz = 5; //goal 21

function setupQuizControls() {
  document.getElementById("language").addEventListener("change", (e) => selectedLang = e.target.value);
  document.getElementById("level").addEventListener("change", (e) => selectedLevel = e.target.value);
  document.getElementById("startButton").addEventListener("click", startQuiz);
}

// Verbesserte Funktion zum Laden der Fragen mit korrektem Content-Type
async function loadQuestions() { 
    try {
        // Fetch mit expliziter Angabe für den Response-Type
        const res = await fetch(`lang/${selectedLang}.json`, {
            headers: {
                'Accept': 'application/json; charset=utf-8'
            }
        });
        
        // Den Response als JSON dekodieren
        const data = await res.json();
        
        const filtered = data.filter(q => q.difficulty.includes(selectedLevel));
        let extended = [...filtered];
        while (extended.length < maxQuestionsPerQuiz) {
            extended.push(...shuffle(filtered));
        }
        return shuffle(extended).slice(0, maxQuestionsPerQuiz);
    } catch (error) {
        console.error("Fehler beim Laden der Fragen:", error);
        return [];
    }
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
    const translations = {
        de: {
            score: "Score",
            perfect: "Perfekt! 🎉 Du hast alles richtig beantwortet.",
            wrongAnswers: "Falsche Antworten:",
            question: "Frage",
            yourAnswer: "Deine Antwort",
            correctAnswer: "Richtige Antwort",
            satoshiLevel: "🟢 Satoshi-Level!",
            bitcoinerLevel: "🟡 Bitcoiner-Level",
            curiousLevel: "🔴 Curious-Level"
        },
        en: {
            score: "Score",
            perfect: "Perfect! 🎉 You answered everything correctly.",
            wrongAnswers: "Wrong Answers:",
            question: "Question",
            yourAnswer: "Your Answer",
            correctAnswer: "Correct Answer",
            satoshiLevel: "🟢 Satoshi Level!",
            bitcoinerLevel: "🟡 Bitcoiner Level",
            curiousLevel: "🔴 Curious Level"
        },
        fr: {
            score: "Score",
            perfect: "Parfait! 🎉 Vous avez tout répondu correctement.",
            wrongAnswers: "Réponses incorrectes:",
            question: "Question",
            yourAnswer: "Votre réponse",
            correctAnswer: "Bonne réponse",
            satoshiLevel: "🟢 Niveau Satoshi!",
            bitcoinerLevel: "🟡 Niveau Bitcoiner",
            curiousLevel: "🔴 Niveau Curieux"
        }
    };

    // Standardsprache ist Deutsch falls etwas nicht stimmt
    const t = translations[selectedLang] || translations.de;
    
    let level;
    const percentage = score / questions.length;
    
    if (percentage >= 0.85) level = t.satoshiLevel;
    else if (percentage >= 0.6) level = t.bitcoinerLevel;
    else level = t.curiousLevel;

    let resultHTML = `<h2>${t.score}: ${score}/${questions.length}</h2>`;
    resultHTML += `<p>${level}</p>`;

    if (wrongAnswers.length > 0) {
        resultHTML += `<h3>${t.wrongAnswers}</h3><ul>`;
        wrongAnswers.forEach((item, index) => {
            resultHTML += `
                <li>
                    <strong>${t.question} ${index + 1}:</strong> ${item.question}<br>
                    <strong>${t.yourAnswer}:</strong> ${item.yourAnswer}<br>
                    <strong>${t.correctAnswer}:</strong> ${item.correctAnswer}
                </li><br>
            `;
        });
        resultHTML += "</ul>";
    } else {
        resultHTML += `<p>${t.perfect}</p>`;
    }

    document.getElementById("quiz").innerHTML = resultHTML;
}

window.setupQuizControls = setupQuizControls;
