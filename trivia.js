const allQuestions = [
  {
    id: 1,
    level: 1,
    en: { q: "What is the smallest unit of Bitcoin?", a: ["Satoshi", "Bit", "Millibit", "Block"], c: 0 },
    de: { q: "Was ist die kleinste Einheit von Bitcoin?", a: ["Satoshi", "Bit", "Millibit", "Block"], c: 0 }
  },
  {
    id: 2,
    level: 2,
    en: { q: "What does HODL mean?", a: ["Hold on for dear life", "Hackers of digital ledgers", "Hard open digital lock"], c: 0 },
    de: { q: "Was bedeutet HODL?", a: ["Hold on for dear life", "Hackers of digital ledgers", "Hard open digital lock"], c: 0 }
  },
  {
    id: 3,
    level: 3,
    en: { q: "What is a hardware wallet?", a: ["Offline storage", "Bitcoin mining rig", "Online exchange"], c: 0 },
    de: { q: "Was ist eine Hardware Wallet?", a: ["Offline-Speicher", "Bitcoin Mining Gerät", "Online-Börse"], c: 0 }
  },
  {
    id: 4,
    level: 4,
    en: { q: "What does a full node do?", a: ["Validates all transactions", "Mines new coins", "Controls the mempool"], c: 0 },
    de: { q: "Was macht ein Full Node?", a: ["Validiert alle Transaktionen", "Mined neue Coins", "Steuert den Mempool"], c: 0 }
  },
  {
    id: 5,
    level: 5,
    en: { q: "What year was the genesis block mined?", a: ["2009", "2008", "2010", "2011"], c: 0 },
    de: { q: "In welchem Jahr wurde der Genesis-Block geschürft?", a: ["2009", "2008", "2010", "2011"], c: 0 }
  },
  // Weitere Fragen kannst du im selben Format ergänzen
];

let currentLang = "en";
document.getElementById("lang").addEventListener("change", e => currentLang = e.target.value);

function startQuiz() {
  const questions = getRandomQuestions(21);
  const container = document.getElementById("quiz-container");
  container.innerHTML = "";

  questions.forEach((q, index) => {
    const langQ = q[currentLang];
    const stars = "★".repeat(q.level);
    const div = document.createElement("div");
    div.className = "question";
    div.innerHTML = `
      <div><strong>Q${index + 1}:</strong> ${langQ.q}</div>
      <div class="stars">${stars}</div>
      <div class="options">
        ${langQ.a.map((opt, i) => `<button onclick="checkAnswer(this, ${i === q[currentLang].c})">${opt}</button>`).join("")}
      </div>
    `;
    container.appendChild(div);
  });
}

function getRandomQuestions(n) {
  const shuffled = allQuestions.sort(() => 0.5 - Math.random());
  return shuffled.slice(0, n);
}

function checkAnswer(btn, correct) {
  btn.style.background = correct ? "green" : "red";
  btn.parentElement.querySelectorAll("button").forEach(b => b.disabled = true);
}
