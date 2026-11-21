
function togglePassword() {
    const passwordField = document.getElementById("password");
    if (!passwordField) return;

    passwordField.type = passwordField.type === "password" ? "text" : "password";
}

// Smooth scrolling for dashboard navigation
document.querySelectorAll('.nav-link[href^="#"], .hero-button[href^="#"]').forEach(link => {
    link.addEventListener("click", function (event) {
        const target = document.querySelector(this.getAttribute("href"));
        if (target) {
            event.preventDefault();
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        }
    });
});

// Set minimum booking time to current time
const dateInputs = document.querySelectorAll('input[type="datetime-local"]');
if (dateInputs.length > 0) {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    const minDate = now.toISOString().slice(0, 16);

    dateInputs.forEach(input => {
        input.min = minDate;
    });
}

// Confirmation before resolving tickets
document.querySelectorAll(".resolve-form").forEach(form => {
    form.addEventListener("submit", function (event) {
        if (!confirm("Mark this maintenance ticket as resolved?")) {
            event.preventDefault();
        }
    });
});
