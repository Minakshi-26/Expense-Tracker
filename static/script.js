// Flash messages auto-hide after 3 sec
setTimeout(() => {
    let alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 500);
    });
}, 3000);

// Chart for Expenses (Pie Chart)
function renderExpenseChart(expenses) {
    if (!expenses.length) return;

    let ctx = document.getElementById("expenseChart").getContext("2d");
    new Chart(ctx, {
        type: "pie",
        data: {
            labels: expenses.map(e => e.category),
            datasets: [{
                data: expenses.map(e => e.amount),
                backgroundColor: ["#3b82f6", "#f59e0b", "#ef4444", "#10b981", "#8b5cf6"]
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { position: "bottom" } }
        }
    });
}
