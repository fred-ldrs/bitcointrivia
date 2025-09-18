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

async function loadQuestions() { 
    try {
        const res = await fetch(`lang/${selectedLang}.json`);
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
    // Intro-Bild ausblenden - verbesserte Version
    const introImage = document.getElementById("intro-image");
    if (introImage) {
        introImage.style.display = "none";
        // Zusätzlich weitere Eigenschaften setzen, um sicherzustellen, dass es wirklich ausgeblendet wird
        introImage.style.visibility = "hidden";
        introImage.classList.add("hidden");
    } else {
        console.warn("Intro-Bild mit ID 'intro-image' wurde nicht gefunden!");
    }
    
    // Quiz-Logik starten
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
            curiousLevel: "🔴 Curious-Level",
            contactInfo: "Für Feedback oder neue Fragen kontaktiere uns bitte unter: info@bitcointrivia.org"
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
            curiousLevel: "🔴 Curious Level",
            contactInfo: "For feedback or new questions, please contact us at: info@bitcointrivia.org"
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
            curiousLevel: "🔴 Niveau Curieux",
            contactInfo: "Pour des commentaires ou de nouvelles questions, contactez-nous à: info@bitcointrivia.org"
        }
    };

    // Standardsprache ist Englisch falls etwas nicht stimmt
    const t = translations[selectedLang] || translations.en;
    
    let level;
    let resultImage;
    const percentage = score / questions.length;
    
    if (percentage >= 0.85) {
        level = t.satoshiLevel;
        resultImage = "assets/images/resultLvl3_V02.png";  // Satoshi Level
    } else if (percentage >= 0.6) {
        level = t.bitcoinerLevel;
        resultImage = "assets/images/resultLvl2_V03.png";  // Bitcoiner Level
    } else {
        level = t.curiousLevel;
        resultImage = "assets/images/resultLvl1_V02.png";  // Curious Level
    }

    let resultHTML = `<h2>${t.score}: ${score}/${questions.length}</h2>`;
    resultHTML += `<p>${level}</p>`;
    resultHTML += `<div class="result-image"><img src="${resultImage}" alt="Result Level Image"></div>`;

    if (wrongAnswers.length > 0) {
        resultHTML += `<h3 style="text-align: left;">${t.wrongAnswers}</h3><ul>`;
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

    // Kontaktinformationen am Ende der Ergebnisseite hinzufügen
    resultHTML += `<div class="contact-info"><p>${t.contactInfo}</p></div>`;

    document.getElementById("quiz").innerHTML = resultHTML;
}

window.setupQuizControls = setupQuizControls;
