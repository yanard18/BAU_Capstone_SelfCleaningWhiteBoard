const canvas    = document.getElementById('canvas');
const ctx       = canvas.getContext('2d');
const submitBtn = document.getElementById('submit-btn');
const resetBtn  = document.getElementById('reset-btn');
const statusEl  = document.getElementById('status');
const resultImg = document.getElementById('result-img');
const backLink  = document.getElementById('back-link');

let points = [];

// Canvas is set to native image resolution; CSS then scales it to fit the viewport.
// Clicks are scaled back to native coordinates before being sent to the server.
const boardImage = new Image();
boardImage.src = '/image';
boardImage.onload = () => {
    canvas.width  = boardImage.naturalWidth;
    canvas.height = boardImage.naturalHeight;
    ctx.drawImage(boardImage, 0, 0);
};

function redraw() {
    ctx.drawImage(boardImage, 0, 0);
    points.forEach((pt, i) => {
        ctx.beginPath();
        ctx.arc(pt.x, pt.y, 10, 0, 2 * Math.PI);
        ctx.fillStyle = 'rgba(220, 38, 38, 0.85)';
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 18px sans-serif';
        ctx.fillText(i + 1, pt.x + 14, pt.y + 6);
    });
}

canvas.addEventListener('click', (e) => {
    if (points.length >= 4) return;
    const rect   = canvas.getBoundingClientRect();
    const scaleX = canvas.width  / rect.width;
    const scaleY = canvas.height / rect.height;
    points.push({
        x: Math.round((e.clientX - rect.left) * scaleX),
        y: Math.round((e.clientY - rect.top)  * scaleY),
    });
    redraw();
    const n = points.length;
    submitBtn.textContent = `Submit (${n} / 4)`;
    submitBtn.disabled    = n < 4;
    statusEl.textContent  = n < 4
        ? `${4 - n} corner(s) remaining...`
        : 'All 4 corners selected. Hit Submit.';
});

resetBtn.addEventListener('click', () => {
    points = [];
    resultImg.classList.add('hidden');
    backLink.classList.add('hidden');
    submitBtn.textContent = 'Submit (0 / 4)';
    submitBtn.disabled    = true;
    statusEl.textContent  = 'Click on the board corners...';
    ctx.drawImage(boardImage, 0, 0);
});

submitBtn.addEventListener('click', async () => {
    statusEl.textContent = 'Processing...';
    submitBtn.disabled   = true;
    try {
        const blob    = await api.postBlob('/calibrate/points', { points });
        resultImg.src = URL.createObjectURL(blob);
        resultImg.classList.remove('hidden');
        backLink.classList.remove('hidden');
        statusEl.textContent = 'Calibration saved. Result shown below.';
    } catch (err) {
        statusEl.textContent = `Error: ${err.message}`;
        submitBtn.disabled   = false;
    }
});
