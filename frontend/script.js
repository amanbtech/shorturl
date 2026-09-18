const email = document.getElementById("email");
const password = document.getElementById("password");
const loginBtn = document.getElementById("loginBtn");
loginBtn.addEventListener("click", async function () {

    const emailValue = email.value;
    const passwordValue = password.value;


    if (!emailValue || !passwordValue) {
        alert("Please enter email and password");
        return;
    }


    try {

        const response = await fetch(
            "http://127.0.0.1:8000/login",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email: emailValue,
                    password: passwordValue
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            alert(data.detail || "Login failed");

            return;
        }


        localStorage.setItem(
            "token",
            data.token
        );


        window.location.href = "dashboard.html";

    }

    catch (error) {

        console.error(error);

        alert("Cannot connect to server");

    }

});