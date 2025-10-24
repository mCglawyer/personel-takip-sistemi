// static/js/main.js

// updateClock fonksiyonu saati ve tarihi alıp HTML'e yazdırır
function updateClock() {
    const now = new Date(); // O anki tarih ve saati al

    // --- Tarihi Formatla (örn: 21 Ekim 2025, Salı) ---
    const dateOptions = {
        weekday: 'long',  // "Salı"
        year: 'numeric',  // "2025"
        month: 'long',    // "Ekim"
        day: 'numeric'    // "21"
    };
    const formattedDate = now.toLocaleDateString('tr-TR', dateOptions);

    // --- Saati Formatla (örn: 09:38:15) ---
    const timeOptions = {
        hour: '2-digit',   // "09"
        minute: '2-digit', // "38"
        second: '2-digit', // "15"
        hour12: false      // 24 saat formatı
    };
    const formattedTime = now.toLocaleTimeString('tr-TR', timeOptions);

    // HTML'deki ilgili yerleri bul ve içlerini doldur
    document.getElementById('date').innerText = formattedDate;
    document.getElementById('time').innerText = formattedTime;
}

// "DOMContentLoaded" olayı, sayfanın HTML'i yüklendiğinde çalışır
// Bu, script'in HTML elemanlarını bulamama hatasını engeller
document.addEventListener('DOMContentLoaded', (event) => {
    // 1. Saati sayfa yüklenir yüklenmez bir kez çalıştır
    updateClock();
    
    // 2. Saatin her saniye (1000ms) kendini güncellemesini sağla
    setInterval(updateClock, 1000);
});