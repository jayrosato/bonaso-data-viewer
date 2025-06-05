export default function createSelect(options=[], text=null, includeNull=false, setAttribute=null, attributeValues=null, search=false){
    const selector = document.createElement('select')
    if(includeNull){
        const nullOption = document.createElement('option');
        nullOption.value = '';
        nullOption.innerText = '-----';
        selector.appendChild(nullOption)
    }
    if(options.length == 0 && !includeNull){
        console.warn('Static select creator requires options!');
        return;
    }
    options.forEach((value, index) => {
        const option = document.createElement('option')
        option.value = value;
        option.innerText = text ? text[index] : value
        if(setAttribute && attributeValues){
            option.setAttribute(setAttribute, attributeValues[index])
        }
        selector.appendChild(option)
    })
    if(search){
        selector.setAttribute('search', 'true')
    }
    return selector
}