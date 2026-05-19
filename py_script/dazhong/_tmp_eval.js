
const result = [];
document.querySelectorAll('a').forEach(a => {
    if (a.textContent.includes('阅读使用维护说明书')) {
        const li = a.closest('li');
        const nameSpan = li ? li.querySelector('.car-name') : null;
        const name = nameSpan ? nameSpan.textContent.trim() : '';
        result.push({name: name, href: a.href, onclick: a.getAttribute('onclick') || '', dataUrl: a.getAttribute('data-url') || ''});
    }
});
JSON.stringify(result);
