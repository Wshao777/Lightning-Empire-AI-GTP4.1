async function refresh() {
    const res = await fetch("/api/status");
    const data = await res.json();

    document.getElementById("nodes").innerText =
        data.nodes;

    document.getElementById("cpu").innerText =
        data.cpu + "%";
}

setInterval(refresh, 3000);
refresh();
