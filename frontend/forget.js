const email=document.getElementById("email")
const btn=document.getElementById("otp")
btn.addEventListener("click",async function(){
    const emailValue=email.value;
    if(!emailValue){
        alert("enter email");
        return;
    }

        const response = await fetch(
            "http://127.0.0.1.8000/forget", {
                method: "POST",
                headers: {
                    "content-type": "application/json"
                },
                body: JSON.stringify({
                    email: emailValue
                })
            })





})