document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("openWaitlistForm").addEventListener("click", function () {
        document.getElementById("waitlist-form").classList.remove("hidden");
    });

    document.getElementById("waitlistSignup").addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission

        let submitButton = this.querySelector("button[type='submit']");
        submitButton.disabled = true; // Prevent multiple clicks

        let formData = {
            name: document.getElementById("name").value.trim(),
            email: document.getElementById("email").value.trim(),
            phone_no: document.getElementById("phone_no").value.trim(),
            country: document.getElementById("country").value.trim(),
            state: document.getElementById("state").value.trim(),
            occupation: document.getElementById("occupation").value.trim(),
        };

        console.log("🚀 Sending form data:", formData);

        try {
            let response = await fetch("/join-waitlist", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData),
            });

            let data = await response.json();
            console.log("🔍 Server response:", data);

            if (response.ok) {
                // ✅ Redirect to the thank-you page and STOP execution
                window.location.href = "/thank-you-waitlist";
                return; // 🛑 This prevents further execution
            } else {
                alert("❌ " + data.message);
            }
        // } catch (error) {
        //     console.error("🚨 Fetch error:", error);
        //     alert("❌ Something went wrong. Please try again.");
        } finally {
            submitButton.disabled = false; // Re-enable button after request
        }
    });
});
