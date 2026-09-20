const otp=document.getElementById("verify-otp")
const btn=document.getElementById("otp")
btn.addEventListener("click",async function(){
    const otpValue=otp.value

    const emaildata=sessionStorage.getItem("email")
    const response=await fetch("http:127.0.0.1:8000/verify_otp",{
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email:emaildata,
                otp_data:otpValue
            })


    })
    window.location.href="resetpassword.html"

})

