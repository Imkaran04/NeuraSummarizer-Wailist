document.getElementById("surveyForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const responses = {}; // Store survey responses as JSON

    document.querySelectorAll("input[type='radio']:checked, input[type='text'], textarea").forEach(input => {
        responses[input.name] = input.value;
    });

    try {
        const response = await fetch("/submit-survey", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, responses })
        });

        const result = await response.json();
        alert(result.message); // Show success or error message

        if (response.ok) {
            window.location.href = "/thank-you"; // Redirect on success
        }
    } catch (error) {
        alert("❌ Something went wrong. Please try again.");
    }
});
