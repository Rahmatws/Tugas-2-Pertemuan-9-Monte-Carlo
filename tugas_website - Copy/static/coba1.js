function showSection(sectionId, event) {
    if (event) event.preventDefault();  // Mencegah perilaku default <a>

    // Sembunyikan semua section
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => section.classList.remove('active'));

    // Tampilkan section yang dipilih
    const selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.classList.add('active');
    }
}

document.getElementById('jurusan-select').addEventListener('change', function () {
    const jurusan = this.value;
    if (jurusan) {
        fetch('/prediksi', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ jurusan: jurusan })
        })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                    return;
                }

                // Update tabel interval
                const intervalTable = document.getElementById('interval-table');
                intervalTable.innerHTML = '';
                data.interval_data.forEach((row, index) => {
                    intervalTable.innerHTML += `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${row.tahun}</td>
                            <td>${row.jumlah}</td>
                            <td>${row.probabilitas}</td>
                            <td>${row.kumulatif}</td>
                            <td>${row.interval[0]} - ${row.interval[1]}</td>
                        </tr>`;
                });

                // Update tabel RNG
                const rngTable = document.getElementById('rng-table');
                rngTable.innerHTML = '';
                data.rng_values.forEach((rng, index) => {
                    rngTable.innerHTML += `
                        <tr>
                            <td>${rng}</td>
                            <td>${(1103515245 * rng + 12345)}</td>
                            <td>${(1103515245 * rng + 12345) % Math.pow(2, 31)}</td>
                            <td>${data.angka_tiga_digit[index]}</td>
                        </tr>`;
                });

                // Update tabel prediksi
                const prediksiTable = document.getElementById('prediksi-table');
                prediksiTable.innerHTML = '';
                data.prediksi.forEach((row, index) => {
                    prediksiTable.innerHTML += `
                        <tr>
                            <td>${row.fakultas}</td>
                            <td>${row.tahun}</td>
                            <td>${row.jumlah}</td>
                        </tr>`;
                });
            })
            .catch(error => console.error('Error:', error));
    }
});


