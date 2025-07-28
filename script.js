let questions = [];
let currentQuestionIndex = 0;
let score = 0;
let totalQuestions = 21;
let currentLang = 'en';

document.getElementById("language").addEventListener("change", async (e) => {
    currentLang = e.target.value;
    await loadQuestions(currentLang);
    startQuiz();
});

async function loadQuestions(lang) {
    const res = await fetch(`lang/${lang}.json`);
    const data = await res.json();
    questions = shuffle(data).slice(0, totalQuestions);
}

function shuffle(array) {
    return array.sort(() => Math.random() - 0.5);
}

function startQuiz() {
    currentQuestionIndex = 0;
    score = 0;
    document.getElementById("result-container").style.display = "none";
    document.getElementById("quiz-container").style.display = "block";
    showQuestion();
}

function showQuestion() {
    const question = questions[currentQuestionIndex];
    document.getElementById("question").textContent = question.q;
    const answersDiv = document.getElementById("answers");
    answersDiv.innerHTML = "";

    question.a.forEach((answer, idx) => {
        const btn = document.createElement("button");
        btn.textContent = answer;
        btn.onclick = () => handleAnswer(idx === question.c, btn);
        answersDiv.appendChild(btn);
    });

    document.getElementById("progress").textContent = `${currentQuestionIndex + 1} / ${totalQuestions}`;
}

function handleAnswer(isCorrect, btn) {
    if (isCorrect) {
        btn.classList.add("correct");
        score++;
    } else {
        btn.classList.add("wrong");
    }

    Array.from(btn.parentElement.children).forEach(b => b.disabled = true);

    setTimeout(() => {
        currentQuestionIndex++;
        if (currentQuestionIndex < totalQuestions) {
            showQuestion();
        } else {
            showResult();
        }
    }, 800);
}

function showResult() {
    document.getElementById("quiz-container").style.display = "none";
    document.getElementById("result-container").style.display = "block";
    document.getElementById("result-title").textContent = "🎉 Finished!";
    document.getElementById("result-score").textContent = `You scored ${score} / ${totalQuestions}`;
}

// Load default language
loadQuestions(currentLang).then(startQuiz);
