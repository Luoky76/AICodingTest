/**
 * Frontend application logic for the Order Extraction & Verification Assistant.
 */

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initForms();
    initSampleData();
});

// --- Tab Navigation ---

function initTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            const targetId = 'tab-' + tab.dataset.tab;
            document.getElementById(targetId).classList.add('active');
        });
    });
}

// --- Form Handling ---

function initForms() {
    // Email form
    document.getElementById('email-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        await submitForm('/api/process-email', formData, true);
    });

    // Excel form
    document.getElementById('excel-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        await submitForm('/api/upload-excel', formData, true);
    });

    // JSON form
    document.getElementById('json-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const jsonText = document.getElementById('json-input').value.trim();
        if (!jsonText) {
            showError('Please enter JSON data');
            return;
        }
        try {
            const data = JSON.parse(jsonText);
            await submitJson('/api/process', data);
        } catch (err) {
            showError('Invalid JSON format: ' + err.message);
        }
    });
}

async function submitForm(url, formData, isMultipart) {
    showLoading();
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
        });
        const data = await response.json();
        if (data.error) {
            showError(data.message);
        } else if (!response.ok) {
            showError(data.message || 'Processing failed');
        } else {
            showResults(data);
        }
    } catch (err) {
        showError('Request failed: ' + err.message);
    }
}

async function submitJson(url, jsonData) {
    showLoading();
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(jsonData),
        });
        const data = await response.json();
        if (data.error) {
            showError(data.message);
        } else if (!response.ok) {
            showError(data.message || 'Processing failed');
        } else {
            showResults(data);
        }
    } catch (err) {
        showError('Request failed: ' + err.message);
    }
}

// --- Display Functions ---

function showLoading() {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').style.display = 'none';
    document.getElementById('error').style.display = 'none';
    document.getElementById('placeholder').style.display = 'none';

    // Disable all submit buttons
    document.querySelectorAll('.btn-primary').forEach(btn => btn.disabled = true);
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
    document.querySelectorAll('.btn-primary').forEach(btn => btn.disabled = false);
}

function showError(message) {
    hideLoading();
    document.getElementById('results').style.display = 'none';
    document.getElementById('placeholder').style.display = 'none';
    const errorEl = document.getElementById('error');
    errorEl.style.display = 'block';
    document.getElementById('error-message').textContent = message;
}

function showResults(data) {
    hideLoading();
    document.getElementById('error').style.display = 'none';
    document.getElementById('placeholder').style.display = 'none';
    const resultsEl = document.getElementById('results');
    resultsEl.style.display = 'block';

    // Status badge
    const statusBadge = document.getElementById('status-badge');
    const status = data.validationResult.finalStatus;
    const statusLabels = { pass: '✅ 通过', fail: '❌ 失败', manual: '⚠️ 需人工确认' };
    statusBadge.textContent = statusLabels[status] || status;
    statusBadge.className = 'status-badge status-' + status;

    // Extracted data
    renderExtractedData(data.extractedData);

    // Validation result
    renderValidationResult(data.validationResult);

    // Suggestion
    document.getElementById('suggestion').textContent = data.suggestion;

    // Raw JSON
    document.getElementById('raw-json').textContent = JSON.stringify(data, null, 2);
}

function renderExtractedData(extracted) {
    const el = document.getElementById('extracted-data');
    let html = '<table>';
    html += `<tr><th>客户名称</th><td>${escapeHtml(extracted.customerName) || '<em>未识别</em>'}</td></tr>`;
    html += `<tr><th>交付日期</th><td>${escapeHtml(extracted.deliveryDate) || '<em>未识别</em>'}</td></tr>`;
    html += `<tr><th>置信度</th><td>${(extracted.confidence * 100).toFixed(1)}%</td></tr>`;
    html += `<tr><th>商品数量</th><td>${extracted.items ? extracted.items.length : 0} 项</td></tr>`;
    html += '</table>';

    if (extracted.items && extracted.items.length > 0) {
        html += '<table class="items-table">';
        html += '<tr><th>序号</th><th>产品编码</th><th>数量</th><th>单价</th><th>小计</th></tr>';
        let total = 0;
        for (let i = 0; i < extracted.items.length; i++) {
            const item = extracted.items[i];
            const subtotal = item.quantity * item.price;
            total += subtotal;
            html += `<tr><td>${i + 1}</td><td>${escapeHtml(item.productCode)}</td><td>${item.quantity}</td><td>${item.price}</td><td>${subtotal.toFixed(2)}</td></tr>`;
        }
        html += `<tr style="font-weight:700;border-top:2px solid #cbd5e1;"><td colspan="4" style="text-align:right;">合计</td><td>${total.toFixed(2)}</td></tr>`;
        html += '</table>';
    } else {
        html += '<p style="color: #9ca3af; margin-top: 8px;">未提取到订单项</p>';
    }

    el.innerHTML = html;
}

function renderValidationResult(validation) {
    const el = document.getElementById('validation-result');
    let html = '<table>';
    html += `<tr><th>最终状态</th><td>${escapeHtml(validation.finalStatus)}</td></tr>`;
    html += `<tr><th>置信度</th><td>${(validation.confidence * 100).toFixed(1)}%</td></tr>`;
    html += '</table>';

    if (validation.issues && validation.issues.length > 0) {
        html += '<ul class="issue-list">';
        for (const issue of validation.issues) {
            html += `<li>${escapeHtml(issue)}</li>`;
        }
        html += '</ul>';
    } else {
        html += '<p style="color: #16a34a; margin-top: 8px;">✅ 所有校验通过</p>';
    }

    el.innerHTML = html;
}

// --- Utility ---

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// --- Sample Data ---

function initSampleData() {
    document.getElementById('fill-sample').addEventListener('click', () => {
        const sample = {
            type: "email",
            subject: "订单 - Acme Corp - 2024年3月",
            body: "Dear Team,\n\n请处理以下订单：\n\n客户: Acme Corp\n交付日期: 2024-06-15\n\n产品列表：\nPROD-001 | 10 | 99.99\nPROD-002 | 5 | 49.99\nPROD-003 | 20 | 29.99\nPROD-004 | 3 | 199.99\n\n谢谢！",
            attachments: []
        };
        document.getElementById('json-input').value = JSON.stringify(sample, null, 2);
    });
}
