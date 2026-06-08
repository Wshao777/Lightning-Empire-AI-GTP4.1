async function sendTask() {
    const node_id = document.getElementById("node").value;
    const cmd = document.getElementById("cmd").value;

    const res = await fetch("/api/task", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({node_id, cmd})
    });

    const data = await res.json();
    document.getElementById("log").innerText += JSON.stringify(data) + "\n";
}
