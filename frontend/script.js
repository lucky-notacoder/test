// ==========================
// LOAD ANIMATION
// ==========================
window.onload = () => {
  document.body.classList.add("loaded");
};

// ==========================
// PAGE TRANSITION
// ==========================
document.querySelectorAll("a").forEach(link => {
  link.addEventListener("click", function(e) {
    if (this.hostname === window.location.hostname) {
      e.preventDefault();
      document.body.classList.remove("loaded");
      setTimeout(() => {
        window.location = this.href;
      }, 300);
    }
  });
});

// ==========================
// PARTICLES (STAR BACKGROUND)
// ==========================
if (typeof particlesJS === "function") {
  particlesJS("particles-js", {
    particles: {
      number: {
        value: 200,
        density: {
          enable: true,
          value_area: 800
        }
      },
      size: {
        value: 2,
        random: true
      },
      color: {
        value: "#ffffff"
      },
      opacity: {
        value: 0.6,
        random: true,
        anim: {
          enable: true,
          speed: 1,
          opacity_min: 0.2,
          sync: false
        }
      },
      line_linked: {
        enable: false
      },
      move: {
        speed: 0.8,
        direction: "none",
        out_mode: "out"
      }
    }
  });
}

// ==========================
// EMAILJS INTEGRATION
// ==========================
const form = document.getElementById("contact-form");
const statusMessage = document.getElementById("form-status");

function playCelebration(target) {
  if (!target) return;

  const burst = document.createElement("div");
  burst.className = "celebration-burst";

  for (let i = 0; i < 18; i += 1) {
    const particle = document.createElement("span");
    particle.className = "celebration-particle";
    particle.style.setProperty("--angle", `${(360 / 18) * i}deg`);
    particle.style.setProperty("--distance", `${70 + Math.random() * 50}px`);
    particle.style.setProperty("--delay", `${Math.random() * 0.15}s`);
    particle.style.setProperty("--hue", `${190 + Math.random() * 80}`);
    burst.appendChild(particle);
  }

  target.appendChild(burst);

  window.setTimeout(() => {
    burst.remove();
  }, 1200);
}

if (form && typeof emailjs !== "undefined") {
  emailjs.init("Rnh7EhqHVuOVgx-RV");

  form.addEventListener("submit", function(e) {
    e.preventDefault();
    const submitButton = form.querySelector('button[type="submit"]');
    const emailField = form.querySelector('input[name="from_email"]');
    const replyToField = form.querySelector('input[name="reply_to"]');

    if (emailField && replyToField) {
      replyToField.value = emailField.value.trim();
    }

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.textContent = "Sending...";
    }

    if (statusMessage) {
      statusMessage.textContent = "";
    }

    emailjs.sendForm("service_fdh2idl", "template_n7617fn", this)
      .then(function(response) {
        if (statusMessage) {
          statusMessage.textContent = "Message sent successfully.";
        }
        console.log("EmailJS success", response);
        form.reset();
        playCelebration(form);
      })
      .catch(function(error) {
        const errorDetails = error?.text || error?.message || error?.status || "Unknown EmailJS error";
        if (statusMessage) {
          statusMessage.textContent = "Failed to send message: " + errorDetails;
        }
        console.error("EmailJS error", error);
      })
      .finally(function() {
        if (submitButton) {
          submitButton.disabled = false;
          submitButton.textContent = "Send";
        }
      });
  });
} else if (form) {
  console.error("EmailJS library did not load on the contact page.");
  if (statusMessage) {
    statusMessage.textContent = "Contact form is unavailable right now because EmailJS did not load.";
  }
}
