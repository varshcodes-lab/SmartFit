const BASE_URL = "https://smartfit-ai-backend.onrender.com";

function getDiet() {
    let w = document.getElementById("weight").value;
    let h = document.getElementById("height").value;

    fetch(`${BASE_URL}/diet?weight=${w}&height=${h}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("dietResult").innerText =
                `BMI: ${data.BMI} | Plan: ${data["Diet Plan"]}`;
        });
}

function getPerformance() {
    let c = document.getElementById("correct").value;
    let t = document.getElementById("total").value;
    let time = document.getElementById("time").value;

    fetch(`${BASE_URL}/performance?correct=${c}&total=${t}&time=${time}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("performanceResult").innerText =
                `Performance Score: ${data["Performance Score"]}`;
        });
}

function getHabit() {
    let g = document.getElementById("gap").value;
    let m = document.getElementById("missed").value;

    fetch(`${BASE_URL}/habit?days_gap=${g}&missed=${m}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("habitResult").innerText =
                `Skip Probability: ${data["Skip Probability"]}`;
        });
}

function talkBuddy() {
    let msg = document.getElementById("message").value;

    fetch(`${BASE_URL}/buddy?message=${msg}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("buddyResult").innerText =
                data.Response;
        });
}

function getIoT() {
    fetch(`${BASE_URL}/iot`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("iotResult").innerText =
                JSON.stringify(data, null, 2);
        });
}
