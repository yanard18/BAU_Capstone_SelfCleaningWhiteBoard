function debounce(fn, delay) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), delay);
    };
}

function buildSlider(key, { value, min, max, step, label, unit }) {
    const div = document.createElement('div');
    div.className = 'flex flex-col gap-1';
    div.innerHTML = `
        <div class="flex justify-between items-baseline">
            <span class="text-xs text-base-content/60">${label}</span>
            <span class="text-xs font-mono font-semibold" id="val-${key}">${value}${unit ? ' ' + unit : ''}</span>
        </div>
        <input type="range"
               class="range range-xs range-primary"
               data-config="${key}"
               data-unit="${unit}"
               min="${min}" max="${max}" step="${step}" value="${value}">
    `;
    return div;
}

function buildToggle(key, { value, label }) {
    const div = document.createElement('div');
    div.className = 'flex items-center justify-between';
    div.innerHTML = `
        <span class="text-xs text-base-content/60">${label}</span>
        <input type="checkbox" class="toggle toggle-primary toggle-xs"
               data-config="${key}" ${value ? 'checked' : ''}>
    `;
    return div;
}

function populateGroups(config) {
    document.querySelectorAll('[data-config-group]').forEach(el => { el.innerHTML = ''; });
    Object.entries(config).forEach(([key, field]) => {
        const group = document.querySelector(`[data-config-group="${field.group}"]`);
        if (!group) return;
        group.appendChild(field.type === 'bool' ? buildToggle(key, field) : buildSlider(key, field));
    });
}

async function initConfig() {
    const config = await api.get('/config');
    populateGroups(config);
}

// Debounced server POST — fires 150ms after the last interaction.
const _sendConfig = debounce(async (key, value) => {
    try {
        const updated = await api.post('/config', { [key]: value });
        // Sync range inputs back — server may have snapped the value (e.g. odd-number constraint).
        const field = updated[key];
        if (field.type === 'range') {
            const label  = document.getElementById(`val-${key}`);
            const slider = document.querySelector(`[data-config="${key}"]`);
            if (label)  label.textContent = field.value + (field.unit ? ' ' + field.unit : '');
            if (slider) slider.value      = field.value;
        }
    } catch (err) {
        console.error(`Config update failed for "${key}":`, err);
    }
}, 150);

// Single event listener handles both sliders (input) and checkboxes (change).
document.getElementById('dashboard-view').addEventListener('input', e => {
    const key = e.target.dataset.config;
    if (!key) return;

    if (e.target.type === 'checkbox') {
        _sendConfig(key, e.target.checked);
    } else {
        const unit  = e.target.dataset.unit || '';
        const label = document.getElementById(`val-${key}`);
        if (label) label.textContent = e.target.value + (unit ? ' ' + unit : '');
        _sendConfig(key, e.target.value);
    }
});
