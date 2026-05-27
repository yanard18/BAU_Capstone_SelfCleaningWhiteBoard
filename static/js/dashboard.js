async function init() {
    try {
        const { calibrated } = await api.get('/status');
        const badge = document.getElementById('calib-badge');

        if (calibrated) {
            badge.className     = 'badge badge-success gap-1';
            badge.textContent   = '● Calibrated';
            document.getElementById('uncalibrated-view').classList.add('hidden');
            document.getElementById('dashboard-view').classList.remove('hidden');
            document.getElementById('live-feed').src  = '/stream/output';
            document.getElementById('right-feed').src = '/stream/ink_mask';
            await initConfig();
        } else {
            badge.className     = 'badge badge-error gap-1';
            badge.textContent   = '✗ Not Calibrated';
            document.getElementById('uncalibrated-view').classList.remove('hidden');
            document.getElementById('dashboard-view').classList.add('hidden');
        }
    } catch (err) {
        console.error('Failed to fetch status:', err);
    }
}

// Right panel view tabs — switches the stream src without reloading the page.
const rightFeed = document.getElementById('right-feed');
document.querySelectorAll('[data-view]').forEach(tab => {
    tab.addEventListener('click', e => {
        document.querySelectorAll('[data-view]').forEach(t => t.classList.remove('tab-active'));
        e.currentTarget.classList.add('tab-active');
        rightFeed.src = `/stream/${e.currentTarget.dataset.view}`;
    });
});

// Each toggle sends its new state to the server.
// On failure the toggle is reverted so the UI stays in sync with reality.
document.querySelectorAll('[data-debug]').forEach(toggle => {
    toggle.addEventListener('change', async (e) => {
        const name    = e.target.dataset.debug;
        const enabled = e.target.checked;
        try {
            await api.post(`/debug/${name}`, { enabled });
        } catch (err) {
            e.target.checked = !enabled;
            console.error(`Failed to set debug flag "${name}":`, err);
        }
    });
});

init();
