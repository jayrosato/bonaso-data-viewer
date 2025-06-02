export function addWarning(text){
    const warnings = document.querySelector('.warnings');
    const msg = document.createElement('li');
    msg.innerHTML = text;
    warnings.appendChild(msg);
}
export function clearWarning(){
    const warnings = document.querySelector('.warnings');
    warnings.style.border = ''
    warnings.style.backgroundColor = ''
    const msgs = warnings.querySelectorAll('li');
    msgs.forEach(msg => msg.remove())
}
export function initWarning(){
    const warnings = document.querySelector('.warnings');
    warnings.style.border = '5px solid red'
    warnings.style.backgroundColor = 'lightcoral'
}