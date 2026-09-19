const otp=document.getElementById("verify-otp")
const btn=document.getElementById("otp")
btn.addEventListener("click",async function(){
    const otpValue=otp.value
    const response=await fetch("http:127.0.0.1:8000/verify_otp",{
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                otp_data:otpValue
            })


    })
    window.location.href="http://localhost:63342/PythonProject6/frontend/resetpassword.html?_ijt=4mfbbr3qrjsfflnv2gma8hbi66&_ij_reload=RELOAD_ON_SAVE"

})

