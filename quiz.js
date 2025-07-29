let questions = [];
let currentQuestion = 0;
let score = 0;
let selectedLang = "de";
let selectedLevel = "curious";
let wrongAnswers = [];

document.getElementById("language").addEventListener("change", (e) => selectedLang = e.target.value);
document.getElementById("level").addEventListener("change", (e) => selectedLevel = e.target.value);

async function loadQuestions() {
    const res = await fetch(`lang/${selectedLang}.json`);
    const data = await res.json();
    const filtered = data.filter(q => q.difficulty.includes(selectedLevel));
    while (filtered.length < 21) {
        filtered.push(...filtered);
    }
    return shuffle(filtered).slice(0, 21);
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
    showQuestion();
}

function showQuestion() {
    const q = questions[currentQuestion];
    const container = document.getElementById("quiz");
    container.innerHTML = `<p><b>${currentQuestion + 1}/21:</b> ${q.question}</p>` +
        q.options.map((opt, i) =>
            `<button onclick="checkAnswer(${i})">${opt}</button>`
        ).join("<br>");
}

function checkAnswer(answerIndex) {
    const question = questions[currentQuestion];
    const correct = question.answer === answerIndex;

    if (correct) {
        score++;
    } else {
        wrongAnswers.push({
            question: question.question,
            selected: question.options[answerIndex],
            correct: question.options[question.answer]
        });
    }

    currentQuestion++;

    if (currentQuestion < 21) {
        showQuestion();
    } else {
        let resultHTML = `<h2>Score: ${score}/21</h2>` +
            `<p>${score >= 18 ? "🟢 Satoshi-Level!" : score >= 12 ? "🟡 Bitcoiner-Level" : "🔴 Curious-Level"}</p>`;

        if (wrongAnswers.length > 0) {
            resultHTML += `<h3>Falsche Antworten:</h3><ul>`;
            wrongAnswers.forEach(w => {
                resultHTML += `<li><b>${w.question}</b><br>Deine Antwort: ❌ ${w.selected}<br>Richtig: ✅ ${w.correct}</li><br>`;
            });
            resultHTML += `</ul>`;
        }

        document.getElementById("quiz").innerHTML = resultHTML;
    }
}
