setTimeout(function() {
    let alert = document.querySelector('.flash-message');
    if (alert) {
      let fadeEffect = setInterval(function () {
        if (!alert.style.opacity) {
          alert.style.opacity = 1;
        }
        if (alert.style.opacity > 0) {
          alert.style.opacity -= 0.1;
        } else {
          clearInterval(fadeEffect);
          alert.remove();  // Remove from DOM after fadeout
        }
      }, 50);
    }
  }, 3000);