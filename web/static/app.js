async function sendTask() {
    const node = document.getElementById('nodeId').value.trim();
    const cmd = document.getElementById('command').value.trim();
    if (!node || !cmd) {
        alert('请填写 node_id 和 command');
        return;
    }
    const logDiv = document.getElementById('cmdLog');
    logDiv.innerText = `[发送] ${new Date().toLocaleTimeString()} -> ${node}:${cmd}\n等待响应...\n` + logDiv.innerText;

    try {
        const res = await fetch('/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ node_id: node, command: cmd })
        });
        const data = await res.json();
        logDiv.innerText = `[响应] ${new Date().toLocaleTimeString()} -> ${JSON.stringify(data)}\n` + logDiv.innerText;
    } catch (err) {
        logDiv.innerText = `[错误] ${err.message}\n` + logDiv.innerText;
    }
}
