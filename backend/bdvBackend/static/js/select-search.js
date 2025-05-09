document.addEventListener('DOMContentLoaded', function () {
    setTimeout(addSearch, 100) //slight delay to ensure that any other scripts that may create selects on load have completed
});

function addSearch(){
    const selects = document.querySelectorAll('select')
    selects.forEach((select) => {
        let selectParent = select.parentElement
        let selectLoc = selectParent.nodeName.toLocaleLowerCase();
        if(selectLoc == 'th'){
            let checkSearch = selectParent.getAttribute('sort')
            if(checkSearch != 'text'){
                return
            }
        }
        const search = document.createElement('input')
        search.setAttribute('type', 'text')
        search.setAttribute('class', 'select-search')
        search.onkeydown = () => updateSearch(search, select)
        search.setAttribute('placeholder', 'Start typing to search...')
        select.parentElement.insertBefore(search, select)
        search.style.display = 'none'
        select.onclick = () => displaySearch(search)
    })
}

function displaySearch(search){
    search.style.display = ''
}

function updateSearch(search, select){
    const searchValue = search.value.trim().toLowerCase()
    const options = select.querySelectorAll('option')
    options.forEach((option) => {
        const optionText = option.innerText.trim().toLowerCase()
        if(optionText.includes(searchValue) || searchValue == '' || optionText == '-----'){
            option.style.display = ''
        }
        else{
            option.style.display = 'none'
        }
    })
         
}