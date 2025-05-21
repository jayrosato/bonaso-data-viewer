import { applyFilter } from "./sort-filter-tables.js"
export default function createFilter(type, header, index){
    const filter = document.createElement('div')
    filter.setAttribute('class', 'filter')
    filter.style.backgroundImage = "url('/static/images/filter-outline.svg')";
    let table = document.querySelector('.sortable-table');
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)
    
    //create 'filter panel' that displays the actual values
    const filterOptions = document.createElement('div')
    filterOptions.setAttribute('class', 'filterOptions')
    filterOptions.style.backgroundColor = 'white'
    filterOptions.style.color = 'black'
    filterOptions.style.display = 'none'; //hide by default

    //create search bar to help sort through options
    if(type == 'value'){
        const search = document.createElement('input')
        search.setAttribute('type', 'text')
        search.setAttribute('placeholder', 'Start typing to search...')
        search.onkeyup = () => {
            searchFilter(search, filterOptions);
            applyFilter(index, filter, type);

        }
        filterOptions.appendChild(search)

    }
    //create a button to clear all options
    const clearFilter = document.createElement('button')
    clearFilter.innerText = 'Clear Filter'
    clearFilter.onclick = () => {
        const filters = filterOptions.querySelectorAll('input')
        filters.forEach(filter => {
            filter.checked = false;
            if(filter.getAttribute('type') == 'number' || filter.getAttribute('type') == 'date'){
                filter.remove()
            }
        })
        applyFilter(index, filter, type)
    }
    filterOptions.appendChild(clearFilter)
    
    filter.appendChild(filterOptions)
    let values = []
    let labels = []
    if(type == 'value'){
        rowsArray.forEach((row) => {
            const value = row.cells[index].textContent
            if(!values.includes(value)){
                values.push(value)
            } 
            if(!labels.includes(value)){
                labels.push(value)
            }
        })
    }
    if(type == 'number' || type == 'date'){
        values = ['EQUAL TO', 'GREATER THAN', 'LESS THAN', 'BETWEEN']
        labels = ['EQUAL TO', 'GREATER THAN', 'LESS THAN', 'BETWEEN']
        if(type == 'date'){labels = ['ON', 'AFTER', 'BEFORE', 'BETWEEN']}
    }

    values.forEach((value, valueIndex) => {
        const option = document.createElement('div')
        option.style.display = 'flex'
        option.style.flexDirection = 'row'
        const selectButton = document.createElement('input')
        if(type == 'value'){
            selectButton.setAttribute('type', 'checkbox')
            selectButton.onclick = () => applyFilter(index, filter, type)
        }
        else{
            selectButton.setAttribute('type', 'radio')
            selectButton.setAttribute('name', header.innerText)
            selectButton.onclick = () => {
                showInputs(option, type, index)
                applyFilter(index, filter, type)
            }
        }
        selectButton.value = value
        option.appendChild(selectButton)

        const label = document.createElement('label')
        label.innerText = labels[valueIndex]
        option.appendChild(label)
        filterOptions.appendChild(option)
    })
    filter.onclick = () => {
        const toggleDisplay = filterOptions.style.display == '' ? true : false;
        if(toggleDisplay){
            filterOptions.style.display = ''
            
        }
        else{
            filterOptions.style.display = ''
            document.addEventListener('click', function(event) {
                if (filterOptions && !filterOptions.contains(event.target) && !filter.contains(event.target)) {
                    filterOptions.style.display = 'none';
                }
            });
        }
    }
    return filter;
}

function showInputs(option, type, index){
    const filterOptions = option.parentElement.parentElement
    const filter = filterOptions.parentElement.querySelector('.filter')
    console.log(filter)
    const decimateOptions = filterOptions.querySelectorAll('.input, .input2')
    decimateOptions.forEach(option => option.remove())
    const selectButton = option.querySelector('[type="radio"]')
    const value = selectButton.value
    const input = document.createElement('input')
    input.setAttribute('class', 'input')
    input.type = type == 'number' ? ('number') : ('date')
    input.onkeyup = () => applyFilter(index, filter, type)
    option.appendChild(input)
    if(value == 'BETWEEN'){
        const input2 = document.createElement('input')
        input2.type = type == 'number' ? ('number') : ('date')
        input2.setAttribute('class', 'input2')
        input2.onkeyup = () => applyFilter(index, filter, type)
        option.appendChild(input2)
    }
}

function searchFilter(search, filterOptions){
    const searchValue = search.value.trim().toLowerCase()
    const checks = filterOptions.querySelectorAll('[type="checkbox"]')
    checks.forEach(check =>{
        const checkValue = check.value.trim().toLowerCase()
        if(searchValue == '' || checkValue.includes(searchValue)){
            check.parentElement.style.display = '';
            check.checked = true;
        }
        else{
            check.parentElement.style.display = 'none';
            check.checked == false
        }
    })
}