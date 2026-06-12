(function () {
  const labels = {
    easy: "Easy",
    medium: "Medium",
    hard: "Hard",
  };

  function setMessage(text) {
    const msgBar = document.getElementById("msg-bar");
    if (msgBar) {
      msgBar.textContent = text;
    }
  }

  window.chooseDifficulty = function chooseDifficulty(difficulty, button) {
    if (!labels[difficulty]) {
      console.warn("Invalid difficulty:", difficulty);
      return;
    }

    // Store difficulty immediately
    localStorage.setItem("redAlertMiniDifficulty", difficulty);
    setMessage(labels[difficulty] + " campaign selected. Deploying forces...");

    // Disable buttons after click is processed
    window.requestAnimationFrame(() => {
      document.querySelectorAll(".diff-btn").forEach((btn) => {
        btn.classList.remove("selected");
        btn.disabled = true;
      });

      if (button) {
        button.classList.add("selected");
      }
    });

    // Start game after transition
    window.setTimeout(() => {
      document.body.classList.add("game-started");
      setMessage("Difficulty: " + labels[difficulty] + ". Awaiting orders, Commander.");
    }, 450);
  };

  window.addEventListener("keydown", (event) => {
    const keyMap = {
      "1": "easy",
      "2": "medium",
      "3": "hard",
    };

    if (keyMap[event.key] && !document.body.classList.contains("game-started")) {
      const button = document.querySelector(
        ".diff-btn[onclick*=\"" + keyMap[event.key] + "\"]"
      );
      window.chooseDifficulty(keyMap[event.key], button);
    }
  });
})();
