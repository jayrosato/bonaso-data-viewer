import createFilter from "./create-filter.js";
import { createButtons, showPage, recalculatePage } from "./table-pages.js";

document.addEventListener('DOMContentLoaded', async function () {
    addClickable()
    const search = document.querySelector('.search-records')
    createFilters()
    createButtons()
    showPage()
});

let check = [] //{row:int, col:int, bool:t/f}
function createFilters(){
    let table = document.querySelector('.sortable-table');
    if(!table){
        return
    }
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)
    const headers = table.querySelectorAll('.headerDiv')
    headers.forEach((header, index) =>{
        const checkFilter = header.getAttribute('filter')
        if(checkFilter){
            rowsArray.forEach((row, rowIndex) => {
                check.push({'row':rowIndex, 'col':index, 'show':true})
            })
            const filter = createFilter(checkFilter, header, index)
            header.appendChild(filter)
            filter.onchange = () => applyFilter(index, filter, checkFilter)
        }
    })
}

export function applyFilter(col, filter, type){
    let table = document.querySelector('.sortable-table');
    const headers = table.querySelectorAll('th')
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)
    const filterOptions = filter.parentElement.parentElement.querySelector('.filterOptions')
    let filterValues = null;
    let comparison = null;
    if(type == 'number' || type == 'date'){
        
        if(comparison == 'BETWEEN'){
            let value1 = filter.querySelector('.input') ? filter.querySelector('.input').value : ''
            let value2 = filter.querySelector('.input2') ? filter.querySelector('.input2').value : ''
            filterValues = {'lower':value1, 'upper':value2}
        }
        else{
            filterValues = filter.querySelector('.input') ? filter.querySelector('.input').value : ''
        }
    }
    let checkEmpty = false
    if(type == 'value'){
        filterValues = []
        const inputs = filterOptions.querySelectorAll('input')
        inputs.forEach(input => {
            if(input.getAttribute('type') == 'date' || input.getAttribute('type') == 'number'){
                return;
            }
            const value = input.checked ? input.value : null
            if(value){filterValues.push(value)}
        });

        if(filterValues.length == 0){checkEmpty = true}
        else{
            rowsArray.forEach((row, index) => {
                let value = row.cells[col].textContent
                if(filterValues.includes(value)){
                    const toClear = check.filter(cell => (cell.row == index && cell.col == col))
                    toClear.forEach((cell) => cell.show = true)
                }
                else{
                    const toClear = check.filter(cell => (cell.row == index && cell.col == col))
                    toClear.forEach((cell) => cell.show = false)
                }
            });
        }
    }
    else if(type == 'date' || type == 'number'){
        let comparison = '';
        const inputs = filterOptions.querySelectorAll('[type="radio"]')
        for (let input of inputs) {
            if (input.checked && input.value) {
                comparison = input.value;
                break;
            }
        }
        let input = filter.parentElement.querySelector('.input') ? filter.parentElement.querySelector('.input').value : '';
        let input2 = ''
        if(!input || comparison == ''){checkEmpty = true}
        else{
            if(type == 'date'){
                input = new Date(input)
                input.setHours(0,0,0,0)
                input = input.getTime()
            }
            if(type == 'number'){
                input = parseInt(input)
            }
            if(comparison == 'BETWEEN'){
                input2 = filter.parentElement.querySelector('.input2') ? filter.parentElement.querySelector('.input2').value : '';
                if(input2 == ''){comparison = 'GREATER THAN'}
                else{
                    if(type == 'date'){
                        input2 = new Date(input2)
                        input2.setHours(0,0,0,0)
                        input2 = input2.getTime()
                    }
                    if(type == 'number'){
                        input2 = parseInt(input2)
                    }
                }
            }
            rowsArray.forEach((row, index) => {
                let value = row.cells[col].textContent
                if (type == 'number') {
                    value = parseInt(value);
                } 
                else if (type == 'date') {
                    value = value.replace(/\b(a|p)\.m\./i, (match, p1) => p1.toUpperCase() + "M");
                    value = new Date(value);
                    value.setHours(0,0,0,0)
                    value = value.getTime()
                } 
                if(comparison == 'GREATER THAN' && value > input){
                    const toClear = check.filter(cell => (cell.row == index && cell.col == col))
                    toClear.forEach((cell) => cell.show = true)
                }
                else if(comparison == 'LESS THAN' && value < input){
                    const toClear = check.filter(cell => (cell.row == index && cell.col == col))
                    toClear.forEach((cell) => cell.show = true)
                }
                else if(comparison == 'EQUAL TO' && value == input){
                    const toClear = check.filter(cell => (cell.row == index && cell.col == col))
                    toClear.forEach((cell) => cell.show = true)
                }
                else if(comparison == 'BETWEEN' && value >= input && value <= input2){
                    const toClear = check.filter(cell => (cell.row == index && cell.col == col))
                    toClear.forEach((cell) => cell.show = true)
                }
                else if(comparison == ''){checkEmpty = true}
                else{
                    const toClear = check.filter(cell => (cell.row == index && cell.col == col))
                    toClear.forEach((cell) => cell.show = false)
                }
            });

        }
    }  
    if(checkEmpty == true){
        rowsArray.forEach((row, index) => {
            const toClear = check.filter(cell => (cell.row == index && cell.col == col))
            toClear.forEach((cell) => cell.show = true)
        })
    }
    checkRows()
    if(filterValues == '' || filterValues.length == 0){
        filter.style.backgroundImage = "url('/static/images/filter-outline.svg')";
    }
    else{
        filter.style.backgroundImage = "url('/static/images/filter-check.svg')";
    }
    recalculatePage();
}

function checkRows(){
    let table = document.querySelector('.sortable-table');
    const headers = table.querySelectorAll('.headerDiv')
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

function addClickable(){
    let table = document.querySelector('.sortable-table');
    if(!table){
        return
    }
    let headerTracker = []
    const headers = table.querySelectorAll('.headerDiv')
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
    recalculatePage();
}

export { check as 'filtered' }