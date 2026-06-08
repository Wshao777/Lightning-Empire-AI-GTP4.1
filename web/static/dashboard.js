async function refreshDashboard() {
    try {
        // 获取节点及系统状态
        const statusRes = await fetch('/api/status');
        const status = await statusRes.json();
        document.getElementById('totalNodes').innerText = status.total_nodes;
        document.getElementById('onlineNodes').innerText = status.online_nodes;
        document.getElementById('taskQueue').innerText = status.pending_tasks;
        document.getElementById('avgCpu').innerText = status.avg_cpu + '%';
        document.getElementById('avgRam').innerText = status.avg_ram + '%';

        // 渲染节点表格
        const nodeTbody = document.querySelector('#nodeTable tbody');
        nodeTbody.innerHTML = '';
        status.nodes.forEach(node => {
            const row = `<tr>
                <td>${node.id}</td>
                <td class="${node.status === 'online' ? 'online' : 'offline'}">${node.status}</td>
                <td>${node.cpu}%</td>
                <td>${node.ram}%</td>
                <td>${node.last_heartbeat}</td>
            </tr>`;
            nodeTbody.innerHTML += row;
        });

        // 任务队列表格
        const taskRes = await fetch('/api/tasks');
        const tasks = await taskRes.json();
        const taskTbody = document.querySelector('#taskTable tbody');
        taskTbody.innerHTML = '';
        tasks.forEach(task => {
            const row = `<tr>
                <td>${task.id}</td>
                <td>${task.node_id}</td>
                <td>${task.command}</td>
                <td>${task.status}</td>
            </tr>`;
            taskTbody.innerHTML += row;
        });
    } catch (err) {
        console.error('刷新失败', err);
    }
}

// 每3秒刷新一次
setInterval(refreshDashboard, 3000);
refreshDashboard();
