document.addEventListener('DOMContentLoaded', function () {
    setTimeout(addSearch, 100) //slight delay to ensure that any other scripts that may create selects on load have completed
});

function addSearch(){
    const selects = document.querySelectorAll('select')
    selects.forEach((select) => {
        if(select.getAttribute('search') == 'no'){
            return
        }
        let selectParent = select.parentElement
        const search = document.createElement('input')
        /*
        const searchList = document.createElement('datalist')
        select.querySelectorAll('option').forEach(option => {
            const searchItem = option.cloneNode()
            searchList.appendChild(searchItem)
        })
        selectParent.appendChild(searchList)
        */
        search.setAttribute('type', 'text')
        search.setAttribute('class', 'selectSearch')
        search.onkeydown = () => updateSearch(search, select)
        search.setAttribute('placeholder', 'Start typing to search...')
        select.parentElement.insertBefore(search, select)
        search.style.display = 'none'
        select.onclick = () => displaySearch(search, select)
        selectParent.appendChild(search)
    })
}

function displaySearch(search, select){
    search.style.display = ''
    document.addEventListener('click', function(event) {
        if (search && !search.contains(event.target) && !select.contains(event.target)) {
            search.style.display = 'none';
        }
    });
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