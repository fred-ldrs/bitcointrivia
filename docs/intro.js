<!-- Intro-Overlay -->
<div id="intro-overlay">
  <div class="intro-content">
    <img src="assets/images/IntroV01.png" alt="Satoshi Quizmaster" class="intro-figure" />
    <h1>Can you outsmart Satoshi?</h1>
    <button id="start-quiz">Start Quiz</button>
    <p id="countdown" style="margin-top:0.5rem; font-size:0.9rem; opacity:0.7;">
      Auto-starts in 5 seconds...
    </p>
  </div>
</div>

<style>
  #intro-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.9);
    color: #fff;
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 9999;
  }
  .intro-content {
    text-align: center;
    max-width: 400px;
  }
  .intro-figure {
    max-width: 200px;
    margin-bottom: 1rem;
  }
  #start-quiz {
    background: #f7931a; /* Bitcoin Orange */
    border: none;
    padding: 0.8rem 1.5rem;
    font-size: 1.2rem;
    color: #fff;
    border-radius: 8px;
    cursor: pointer;
  }
  #start-quiz:hover {
    background: #e67e00;
  }
</style>

<script>
  document.addEventListener("DOMContentLoaded", () => {
  const overlay = document.getElementById("intro-overlay");
  const btn = document.getElementById("start-quiz");
  const countdownEl = document.getElementById("countdown");

  const seen = localStorage.getItem("introSeen");
  const now = Date.now();
  const THIRTY_DAYS = 30 * 24 * 60 * 60 * 1000; // ms

  // Intro nur anzeigen, wenn es noch nicht gesehen wurde oder älter als 30 Tage ist
  if (seen) {
    const seenTime = parseInt(seen, 10);
    if (now - seenTime < THIRTY_DAYS) {
      overlay.style.display = "none";
      return;
    }
  }

  function closeIntro() {
    overlay.style.display = "none";
    localStorage.setItem("introSeen", Date.now().toString());
  }

  btn.addEventListener("click", closeIntro);

  let seconds = 5;
  const timer = setInterval(() => {
    seconds--;
    countdownEl.textContent = `Auto-starts in ${seconds} second${seconds !== 1 ? "s" : ""}...`;
    if (seconds <= 0) {
      clearInterval(timer);
      closeIntro();
    }
  }, 1000);
});
</script>
