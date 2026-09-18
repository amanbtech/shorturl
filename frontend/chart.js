const  ctx=document.getElementById("clickChart");
new Chart(ctx,{
    type:"line",
    data:{
        labels:["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        datasets:[{
            label:"Clicks",
            data: [250, 400, 350, 600, 850, 700, 950],
            tension: 0.4
        }],
        options:{
            responsive:true
        }
}
})