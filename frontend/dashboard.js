const token=localStorage.getItem("token");
if(!token){
    window.location.href="index.html"
}
const response=await fetch("http://127.0.0.1:8000/dashboard",
    {
        method:"GET",
        headers:{
            "Authorization":`Bearer ${token}`
        }
    }
);
if (!response.ok) {
    if (response.status === 401) {
        localStorage.removeItem("token");
        window.location.href = "login.html";
    }
}
const  data=await response.json()
document.getElementById("totalUrls").textContent=data.stats.total_urls;
document.getElementById("totalClicks").textContent=data.stats.total_clicks;
document.getElementById("activeUrls").textContent=data.stats.active_urls;
document.getElementById("expiredUrls").textContent=data.stats.expired_urls;
document.getElementById("totalUrls").textContent=data.stats.
document.getElementById("introname").textContent=`welcome back, ${data.user.username};
