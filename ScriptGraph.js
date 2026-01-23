const ctx = document.getElementById('myChart').getContext('2d');

// --- DONNÉES INITIALES ---
const stockageClimat = {
    temperature: [{ x: '2024-01-01T12:00:00', y: 20 }],
    humidite: [{ x: '2024-01-01T12:00:00', y: 45 }],
    luminosite: [{ x: '2024-01-01T12:00:00', y: 70 }]
};

const couleurs = {
    temperature: { border: '#e74c3c', bg: 'rgba(231, 76, 60, 0.1)' },
    humidite: { border: '#3498db', bg: 'rgba(52, 152, 219, 0.1)' },
    luminosite: { border: '#f1c40f', bg: 'rgba(241, 196, 15, 0.1)' }
};

// --- CONFIGURATION DU GRAPHIQUE MULTI-COURBES ---
const config = {
    type: 'scatter',
    data: {
        datasets: [
            {
                label: 'Température (°C)',
                id: 'temperature',
                data: stockageClimat.temperature,
                borderColor: couleurs.temperature.border,
                backgroundColor: couleurs.temperature.bg,
                showLine: true, tension: 0.3, pointRadius: 6, fill: false
            },
            {
                label: 'Humidité (%)',
                id: 'humidite',
                data: stockageClimat.humidite,
                borderColor: couleurs.humidite.border,
                backgroundColor: couleurs.humidite.bg,
                showLine: true, tension: 0.3, pointRadius: 6, fill: false
            },
            {
                label: 'Luminosité (Lux)',
                id: 'luminosite',
                data: stockageClimat.luminosite,
                borderColor: couleurs.luminosite.border,
                backgroundColor: couleurs.luminosite.bg,
                showLine: true, tension: 0.3, pointRadius: 6, fill: false
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                type: 'time',
                min: '1940-01-01T00:00:00',
                max: '2026-12-31T23:59:59',
                time: { tooltipFormat: 'dd MMM yyyy HH:mm' }
            },
            y: { min: 0, max: 100 }
        },
        plugins: {
            zoom: {
                limits: {
                    x: {
                        min: new Date('1940-01-01').getTime(),
                        max: new Date('2026-12-31').getTime(),
                        minRange: 3600000 // 1 heure
                    }
                },
                pan: { enabled: true, mode: 'x', onPan: synchroniserSlider },
                zoom: { wheel: { enabled: true }, mode: 'x', onZoom: synchroniserSlider }
            },
            dragData: {
                round: 0,
                onDragStart: (e, datasetIndex) => {
                    // On n'autorise le drag que pour le paramètre sélectionné dans le menu
                    const sel = document.getElementById('paramSelect').value;
                    return myChart.data.datasets[datasetIndex].id === sel;
                },
                onDragEnd: () => myChart.update()
            }
        },
        onClick: (e, elements, chart) => {
            if (elements.length === 0) {
                const canvasPosition = Chart.helpers.getRelativePosition(e, chart);
                const dataX = chart.scales.x.getValueForPixel(canvasPosition.x);
                const dataY = chart.scales.y.getValueForPixel(canvasPosition.y);

                const sel = document.getElementById('paramSelect').value;
                const isLimited = document.getElementById('limitOnePerDay').checked;
                const targetDs = chart.data.datasets.find(ds => ds.id === sel);

                let dateFinale = new Date(dataX);
                isLimited ? dateFinale.setHours(12, 0, 0, 0) : dateFinale.setMinutes(0, 0, 0);

                const index = targetDs.data.findIndex(p => new Date(p.x).getTime() === dateFinale.getTime());
                if (index !== -1) {
                    targetDs.data[index].y = Math.round(dataY);
                } else {
                    targetDs.data.push({ x: dateFinale.toISOString(), y: Math.round(dataY) });
                }
                targetDs.data.sort((a, b) => new Date(a.x) - new Date(b.x));
                chart.update();
            } else {
                // Suppression : on vérifie que l'on clique sur le paramètre actif
                const dsIndex = elements[0].datasetIndex;
                const sel = document.getElementById('paramSelect').value;
                if (chart.data.datasets[dsIndex].id === sel) {
                    chart.data.datasets[dsIndex].data.splice(elements[0].index, 1);
                    chart.update();
                }
            }
        }
    }
};

const myChart = new Chart(ctx, config);

// --- FONCTIONS LOGIQUES ---

function basculerMode() {
    document.getElementById('zoneAvance').style.display = (document.getElementById('modeSelect').value === 'avance') ? 'flex' : 'none';
}

function genererDepuisFormule() {
    const formule = document.getElementById('formuleMath').value;
    const sel = document.getElementById('paramSelect').value;
    const dataset = myChart.data.datasets.find(ds => ds.id === sel).data;
    dataset.length = 0;
    const debut = new Date(); debut.setMinutes(0,0,0);

    try {
        for (let t = 0; t <= 48; t++) {
            const valY = eval(formule.replace(/t/g, t));
            const date = new Date(debut.getTime() + (t * 3600000));
            dataset.push({ x: date.toISOString(), y: Math.max(0, Math.min(100, valY)) });
        }
        myChart.update();
    } catch (e) { alert("Erreur formule : " + e.message); }
}

function appliquerRepetition() {
    const sel = document.getElementById('paramSelect').value;
    const dataset = myChart.data.datasets.find(ds => ds.id === sel).data;
    const count = parseInt(document.getElementById('repeatCount').value);
    const interval = parseInt(document.getElementById('intervalHours').value) * 3600000;

    if (dataset.length < 1 || count <= 1) return;
    const pattern = [...dataset];

    for (let i = 1; i < count; i++) {
        pattern.forEach(p => {
            const d = new Date(new Date(p.x).getTime() + (i * interval));
            if (d.getFullYear() <= 2026) dataset.push({ x: d.toISOString(), y: p.y });
        });
    }
    dataset.sort((a, b) => new Date(a.x) - new Date(b.x));
    myChart.update();
}

// --- NAVIGATION ---
const scrollBar = document.getElementById('scrollBar');
scrollBar.addEventListener('input', (e) => {
    const minL = new Date('1940-01-01').getTime(), maxL = new Date('2026-12-31').getTime();
    const view = myChart.scales.x.max - myChart.scales.x.min;
    let nMin = minL + ((e.target.value / 1000) * (maxL - minL - view));
    myChart.zoomScale('x', { min: nMin, max: nMin + view }, 'none');
});

function synchroniserSlider() {
    const minL = new Date('1940-01-01').getTime(), maxL = new Date('2026-12-31').getTime();
    scrollBar.value = ((myChart.scales.x.min - minL) / (maxL - minL)) * 1000;
}

function resetZoom() { myChart.resetZoom(); synchroniserSlider(); }
function toggleLine() { myChart.data.datasets.forEach(ds => ds.showLine = document.getElementById('showLine').checked); myChart.update(); }
function exporterDonnees() { console.log(stockageClimat); alert("Données JSON exportées en console (F12)"); }
