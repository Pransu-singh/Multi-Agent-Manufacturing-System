async function generate() {
    const product = document.getElementById("product").value;
    document.getElementById("output").innerText = "Generating report...";

    const response = await fetch("http://localhost:8000/generate-report", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({product})
    });

    const data = await response.json();
    document.getElementById("output").innerText = data.report;
}
