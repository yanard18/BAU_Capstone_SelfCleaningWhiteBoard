const api = {
    async get(url) {
        const res = await fetch(url);
        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
        return res.json();
    },

    async post(url, body) {
        const res = await fetch(url, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(body),
        });
        if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
        return res.json();
    },

    // For endpoints that return binary (e.g. /calibrate/points returns a PNG).
    // On error it parses the JSON body for an error message before throwing.
    async postBlob(url, body) {
        const res = await fetch(url, {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify(body),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || `${res.status} ${res.statusText}`);
        }
        return res.blob();
    },
};
