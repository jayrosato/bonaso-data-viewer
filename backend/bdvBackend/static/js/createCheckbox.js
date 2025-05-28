export default function createCheckbox(value, text=null){
    const div = document.createElement('div');
    div.setAttribute('class', 'option');
    div.style.display = 'flex';
    div.style.flexDirection = 'row';
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.value = value;
    div.appendChild(checkbox);
    const label = document.createElement('label');
    label.innerText = text ? text : value;
    div.appendChild(label);
    return div;
}