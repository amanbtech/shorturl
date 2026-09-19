const username = document.getElementById("username");
const password = document.getElementById("password");
const loginBtn = document.getElementById("loginBtn");
loginBtn.addEventListener("click", async function () {

    const userValue = username.value;
    const passwordValue = password.value;


    if (!userValue || !passwordValue) {
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
                    username: userValue,
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