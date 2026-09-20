const pass=document.getElementById("pass");
const conPass=document.getElementById("conpass");
const btn=document.getElementById("otp-verify");
btn.addEventListener("click",async function(){
    const passValue=pass.value;
    const conpassValue=conPass.value;
    const emaildata=sessionStorage.getItem("email")
    if(!passValue===!conpassValue){
        alert("password mismatch")
        return
    }
    const response=await fetch("http://127.0.0.8000/resetpassword",{
        method:"POST",
        headers:{
            "content-type":"application/json"
        },
        body:JSON.stringify({
            email:emaildata,
            password:passValue,
            confirmPassword:conpassValue
        })


    })
    sessionStorage.removeItem("email")
    window.location.href="index.html"
})