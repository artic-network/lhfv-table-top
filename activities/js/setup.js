function setupDateInserts() {
    const params = new URLSearchParams(window.location.search);
    const date = params.get('date');
    let formattedDate  = new Date(date);
    let year = formattedDate.getUTCFullYear();
    Array.from(document.getElementsByClassName('year')).forEach(el => el.textContent = year);
    let month = String(formattedDate.getUTCMonth() + 1).padStart(2, '0');
    let day = String(formattedDate.getUTCDate()).padStart(2, '0');
    let isoDate = `${year}-${month}-${day}`;
    Array.from(document.getElementsByClassName('iso-date')).forEach(el => el.textContent = isoDate);
    let monthLong = new Intl.DateTimeFormat('en', { month: 'long' }).format(formattedDate);
    let textDate = formattedDate.getDate() + ' ' + monthLong + ' ' + formattedDate.getFullYear();
    Array.from(document.getElementsByClassName('date')).forEach(el => el.textContent = textDate);
    let monthShort = new Intl.DateTimeFormat('en', { month: 'short' }).format(formattedDate);
    let shortDate = monthShort + ' ' + formattedDate.getDate();
    Array.from(document.getElementsByClassName('short-date')).forEach(el => el.textContent = shortDate);
}

function setup() {
    setupDateInserts();
}