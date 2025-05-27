export default function createSearchSelector(values=[], labels=null, nullOption=true, runFunc=null){
    const selectorDiv = document.createElement('div');
    selectorDiv.setAttribute('class', 'selectorCont');

    const dropdown = document.createElement('button');
    dropdown.innerText = 'Dropdown';
    dropdown.onclick = () => {
        const toggleDisplay = selector.style.display == '' ? true : false;
        if(toggleDisplay){
            selector.style.display = 'none'
            
        }
        else{
            selector.style.display = ''
            document.addEventListener('click', function(event) {
                if (selectorDiv && !selectorDiv.contains(event.target)) {
                    selector.style.display = 'none';
                }
            });
        }
    }
    selectorDiv.appendChild(dropdown);

    const selector = document.createElement('div');
    selector.setAttribute('class', 'selector');
    selectorDiv.appendChild(selector)

    const selectorSearch = document.createElement('input');
    selectorSearch.setAttribute('class', 'selectorSearch');
    selectorSearch.onkeyup = () => searchSelect(selectorSearch)
    selector.appendChild(selectorSearch);

    if(nullOption){
        values.unshift('')
        if(labels){labels.unshift('-----')}
    }
    const optionsDiv = document.createElement('div');
    optionsDiv.setAttribute('class', 'optionsList')
    values.forEach((value, index) => {
        const option = document.createElement('div');
        option.setAttribute('class', 'option');
        option.innerText = labels ? labels[index] : value;
        option.setAttribute('value', value);
        option.onclick = () => {
            selector.setAttribute('value', value);
            updateSelector(option, runFunc);
        };
        optionsDiv.appendChild(option);
    })
    selector.appendChild(optionsDiv)
    selector.setAttribute('value', '')
    selector.style.display = 'none';
    return selectorDiv;
}

function searchSelect(search){
    const selector = search.parentElement;
    const value = search.value.toLowerCase().trim();
    const options = selector.querySelectorAll('.option')
    options.forEach((option) => {
        if(option.innerText.trim().toLowerCase().includes(value) || value == ''){
            option.style.display = ''
        }
        else{
            option.style.display = 'none'
        }
    })
}
function updateSelector(selected, runFunc){
    const value = selected.getAttribute('value');
    const list = selected.parentElement;
    const options = list.querySelectorAll('.option');
    options.forEach((option) => {
        if(option.getAttribute('value') == value){
            option.style.backgroundColor = 'red';
        }
        else{
            option.style.backgroundColor = '';
        }
    })
    if(runFunc){
        runFunc()
    }
}