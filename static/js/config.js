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
            <span class="text-xs font-mono font-semibold" id="val-${key}">${value}${unit ? ' ' + unit : ''}</span>
        </div>
        <input type="range"
               class="range range-xs range-primary"
               data-config="${key}"
               data-unit="${unit}"
               min="${min}" max="${max}" step="${step}" value="${value}">
    `;
    return div;
}

function populateGroups(config) {
    document.querySelectorAll('[data-config-group]').forEach(el => { el.innerHTML = ''; });
    Object.entries(config).forEach(([key, field]) => {
        const group = document.querySelector(`[data-config-group="${field.group}"]`);
        if (group) group.appendChild(buildSlider(key, field));
    });
}

async function initConfig() {
    const config = await api.get('/config');
    populateGroups(config);
}

// Debounced server POST — fires 150ms after the last slider movement.
const _sendConfig = debounce(async (key, value) => {
    try {
        const updated = await api.post('/config', { [key]: value });
        // Server may have snapped the value (e.g. odd-number constraint).
        // Sync the label and slider to whatever the server settled on.
        const field  = updated[key];
        const label  = document.getElementById(`val-${key}`);
        const slider = document.querySelector(`[data-config="${key}"]`);
        if (label)  label.textContent = field.value + (field.unit ? ' ' + field.unit : '');
        if (slider) slider.value      = field.value;
    } catch (err) {
        console.error(`Config update failed for "${key}":`, err);
    }
}, 150);

// Event delegation: one listener on the dashboard catches all slider input events.
// Works for dynamically added sliders without re-binding.
document.getElementById('dashboard-view').addEventListener('input', e => {
    const key = e.target.dataset.config;
    if (!key) return;

    // Update the label immediately for instant visual feedback while dragging.
    const unit  = e.target.dataset.unit || '';
    const label = document.getElementById(`val-${key}`);
    if (label) label.textContent = e.target.value + (unit ? ' ' + unit : '');

    _sendConfig(key, e.target.value);
});
