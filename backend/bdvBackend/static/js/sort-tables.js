document.addEventListener('DOMContentLoaded', async function () {
    addClickable()
    const search = document.querySelector('.search-records')
    search.addEventListener('change', () => searchRecords())
    createFilters()
});

function createFilters(){
    let table = document.querySelector('.sortable-table');
    const headers = table.querySelectorAll('th')
    headers.forEach((h, index) =>{
        const filter = h.querySelector('select')
        if(filter){
            const tableBody = table.tBodies[0]
            const values = []
            const rowsArray = Array.from(tableBody.rows)
            rowsArray.forEach((row) => {
                let value = row.cells[index].textContent
                if(!values.includes(value))
                values.push(value)
            })
            const defaultOption = document.createElement('option')
            defaultOption.innerText = '-----'
            defaultOption.value = ''
            filter.appendChild(defaultOption)
            values.forEach((value) => {
                const option = document.createElement('option')
                option.innerText = value
                option.value = value
                filter.appendChild(option)
            })
            filter.onchange = () => applyFilter(index, filter)
        }
    })
}

function applyFilter(col, filter){
    const filterValue = filter.value
    let table = document.querySelector('.sortable-table');
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)
    rowsArray.forEach((row) => {
        let value = row.cells[col].textContent
        if(value == filterValue || filterValue == ''){
            row.style.display = ''
        }
        else{
            row.style.display = 'none'
        }
    });
}
function searchRecords(){
    const search = document.querySelector('.search-records')
    const searchValue = search.value.trim().toLowerCase()
    let table = document.querySelector('.sortable-table');
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)
    rowsArray.forEach((row) => {
        let value = row.cells[0].textContent.trim().toLowerCase()
        if(value.includes(searchValue) || searchValue == ''){
            row.style.display = ''
        }
        else{
            row.style.display = 'none'
        }
    });
    
}

function addClickable(){
    let table = document.querySelector('.sortable-table');
    if(!table){
        return
    }
    headerTracker = []
    const headers = table.querySelectorAll('th')
    headers.forEach((h, index) => {
        headerTracker.push({h:true})
        const sorter = h.querySelector('button')
        if(sorter){
            sorter.onclick = () => {
                let sortDir = headerTracker[index]
                headerTracker[index] = !sortDir
                sortTable(index, sortDir)
            }
        }
    })
}

function sortTable(i, asc=true){
    let table = document.querySelector('.sortable-table');
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)
    const headers = table.querySelectorAll('th')
    let sortType = headers[i].getAttribute('sort')
    if(!sortType){sortType='text'}
    
    rowsArray.sort((current, next) => {
        let currentVal = current.cells[i].textContent.trim()
        let nextVal = next.cells[i].textContent.trim()
        if(sortType == 'text'){
            currentVal = currentVal.toLowerCase()
            nextVal = nextVal.toLowerCase()
        }
        if(sortType == 'number'){
            currentVal = parseFloat(currentVal)
            nextVal = parseFloat(nextVal)
        }
        if(sortType == 'date'){
            currentVal = new Date(currentVal)
            nextVal = new Date(nextVal)
            if (isNaN(currentVal) || isNaN(nextVal)) return 0;
        }
        if(currentVal < nextVal) return asc ? -1:1;
        if(currentVal > nextVal) return asc ? 1:-1;
        return 0
    });
    rowsArray.forEach(row => tableBody.appendChild(row));

    headers.forEach((h, index)=>{
        const sorter = h.querySelector('button')
        if(sorter){
            sorter.innerText = sorter.innerText.replace('↑', 'S').replace('↓', 'S')
            index == i ? sorter.innerText = asc ? '↑' : '↓': null;
        }
    })
}