document.addEventListener('DOMContentLoaded', async function () {
    addClickable()
    const search = document.querySelector('.search-records')
    search.addEventListener('change', () => searchRecords())
    createFilters()
});
let check = [] //{row:int, col:int, bool:t/f}
function createFilters(){
    let table = document.querySelector('.sortable-table');
    const headers = table.querySelectorAll('th')
    headers.forEach((h, index) =>{
        const checkFilter = h.getAttribute('filter')
        if(checkFilter){
            const filter = document.createElement('select')
            h.appendChild(filter)
            const tableBody = table.tBodies[0]
            const rowsArray = Array.from(tableBody.rows)
            rowsArray.forEach((row, rowIndex) => {
                check.push({'row':rowIndex, 'col':index, 'show':true})
            })
            const values = []
            if(checkFilter == 'value'){
                rowsArray.forEach((row, rowIndex) => {
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
            }
            if(checkFilter == 'number' || checkFilter == 'date'){
                const operators = ['', 'EQUAL TO', 'GREATER THAN', 'LESS THAN', 'BETWEEN']
                let labels = ['-----', 'EQUAL TO', 'GREATER THAN', 'LESS THAN', 'BETWEEN']
                if(checkFilter == 'date'){labels = ['-----', 'ON', 'AFTER', 'BEFORE', 'BETWEEN']}
                operators.forEach((value, index) =>{
                    const option = document.createElement('option')
                    option.innerText = labels[index]
                    option.value = value
                    filter.appendChild(option)
                })
            }
            filter.onchange = () => applyFilter(index, filter, checkFilter)
        }
        
    })
}
//row-column --> is valid??
//filter --> col[true/false]
//final checker --> col[true/false], vis[show/hide]
//work on better cross applying these, probably rather than directly hiding/showing, set a checker variable and then test for conditions 
function applyFilter(col, filter, type){
    const filterValue = filter.value
    let table = document.querySelector('.sortable-table');
    const headers = table.querySelectorAll('th')
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)
    if(filterValue == ''){
        rowsArray.forEach((row, index) => {
            const toClear = check.filter(cell => (cell.row == index && cell.col == col))
            toClear.forEach((cell) => cell.show = true)
        })
        let inputs = headers[col].querySelectorAll('input')
        if(inputs){
            inputs.forEach((input) => {headers[col].removeChild(input)})
        }
        checkRows()
        return
    }
    if(type=='number' || type == 'date'){
        let inputs = headers[col].querySelectorAll('input')
        if(inputs){
            inputs.forEach((input) => {headers[col].removeChild(input)})
        }
        const num = document.createElement('input')
        type == 'number' ? num.setAttribute('type', 'number') : num.setAttribute('type', 'date')
        headers[col].appendChild(num)
        if(filterValue == 'BETWEEN'){
            const num2 = document.createElement('input')
            type == 'number' ? num2.setAttribute('type', 'number') : num2.setAttribute('type', 'date')
            headers[col].appendChild(num2)
            num.onchange = () => checkRange(type, col, filterValue, num, num2)
            num2.onchange = () => checkRange(type, col, filterValue, num, num2)
        }
        else{num.onchange = () => checkRange(type, col, filterValue, num)}
    }
    else if(type='value'){
        rowsArray.forEach((row, index) => {
            let value = row.cells[col].textContent
            if(type == 'value' && value == filterValue){
                const toClear = check.filter(cell => (cell.row == index && cell.col == col))
                toClear.forEach((cell) => cell.show = true)
            }
            else{
                const toClear = check.filter(cell => (cell.row == index && cell.col == col))
                toClear.forEach((cell) => cell.show = false)
            }
        });
    }
    checkRows()
}

function checkRange(type, col, operator, input1, input2=null){
    let num = input1.value
    if(num == ''){
        const toClear = check.filter(cell => (cell.row == index && cell.col == col))
        toClear.forEach((cell) => cell.show = true)
        return
    }
    let table = document.querySelector('.sortable-table');
    const headers = table.querySelectorAll('th')
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)
    rowsArray.forEach((row, index) => {
        let display = false
        let value = row.cells[col].textContent
        if(type=='number'){
            num = parseFloat(num)
            value = parseFloat(value)
            if(operator == 'EQUAL TO' && value == num){
                display = true
            }
            else if(operator == 'GREATER THAN' && value > num){
                display = true
            }
            else if(operator == 'LESS THAN' && value < num){
                display = true
            }
            else if(operator == 'BETWEEN'){
                let num2 = parseFloat(input2.value)
                if(value >= num && value <= num2){
                    display = true
                }
            }
        }
        else{
            num = new Date(num)
            value = new Date(value)
            num.setHours(0,0,0,0)
            value.setHours(0,0,0,0)
            if(operator == 'EQUAL TO' && value.getTime() == num.getTime()){
                display = true
            }
            else if(operator == 'GREATER THAN' && value.getTime() > num.getTime()){
                display = true
            }
            else if(operator == 'LESS THAN' && +value < +num){
                display = true
            }
            else if(operator == 'BETWEEN'){
                let num2 = input2.value
                num2 = new Date(num2)
                num2.setHours(0,0,0,0)
                if(value >= +num && value <= +num2){
                    display = true
                }
            }
        }
        const toShow = check.filter(cell => (cell.row == index && cell.col == col))
        toShow.forEach((cell) => cell.show = display)
    });
    checkRows()
}

function checkRows(){
    let table = document.querySelector('.sortable-table');
    const headers = table.querySelectorAll('th')
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)
    rowsArray.forEach((row, index) => {
        let checkCells = check.filter(cell => (cell.row == index))
        let show = true
        checkCells.forEach((cell) => {
            if(cell.show == false){show = false}
        })
        if(show == false){
            row.style.display = 'none'
        }
        else if(show == true){
            row.style.display = ''
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
        const checkSort = h.getAttribute('sort')
        if(checkSort){
            const sorter = document.createElement('img')
            sorter.setAttribute('class', 'sort')
            sorter.src = '/static/images/sort.svg'
            h.appendChild(sorter)
            sorter.onclick = () => {
                let sortDir = headerTracker[index]
                headerTracker[index] = !sortDir
                sortTable(index, sortDir)
            }
        }
        const sorter = h.querySelector('.sort')
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
        const sorter = h.querySelector('.sort')
        if(sorter){
            sorter.src = '/static/images/sort.svg'
            index == i ? sorter.src = asc ? '/static/images/sort-ascending.svg' : '/static/images/sort-descending.svg': null;
        }
    })
}