async function init() {
    try {
        const { calibrated } = await api.get('/status');
        const badge = document.getElementById('calib-badge');

        if (calibrated) {
            badge.className     = 'badge badge-success gap-1';
            badge.textContent   = '● Calibrated';
            document.getElementById('uncalibrated-view').classList.add('hidden');
            document.getElementById('dashboard-view').classList.remove('hidden');
            document.getElementById('live-feed').src  = '/stream/raw';
            document.getElementById('right-feed').src = '/stream/output';
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

init();
