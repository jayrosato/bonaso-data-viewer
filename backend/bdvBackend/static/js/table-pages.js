import { filtered } from './sort-filter-tables.js'

let page = 1
let entries = 10
let lastPage = 1
let max = 0
document.addEventListener('DOMContentLoaded', async function () {
    const table = document.querySelector('.sortable-table');
    if(!table){return;}
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)
    rowsArray.forEach((row, index) =>{
        max = index
    })
    lastPage = Math.floor(max / entries) +1
    createButtons();
    showPage();
});


function pageForward(){
    page ++;
    if(page <= lastPage){
        showPage();
    }
}

function pageBack(){
    page --;
    if(page > 0){
        showPage();
    }
}

function createButtons(max){
    const table = document.querySelector('.sortable-table');
    const tableNav = document.createElement('div')
    tableNav.setAttribute('class', 'tableNav')
    table.after(tableNav)

    const prevPage = document.createElement('button')
    prevPage.setAttribute('class', 'prevPage');
    prevPage.innerText = '<'
    prevPage.onclick = () => pageBack()
    const pageNo = document.createElement('p')
    pageNo.setAttribute('class', 'pageNo');
    const nextPage = document.createElement('button')
    nextPage.setAttribute('class', 'nextPage');
    nextPage.onclick = () => pageForward();
    nextPage.innerText = '>'
    tableNav.appendChild(prevPage);
    tableNav.appendChild(pageNo);
    tableNav.appendChild(nextPage);

    const entryDiv = document.createElement('div');
    tableNav.after(entryDiv)
    const ten = document.createElement('button')
    ten.innerText = '10'
    ten.onclick = () => {
        entries = 10;
        recalculatePage();
    }
    entryDiv.appendChild(ten)

    const twenty = document.createElement('button')
    twenty.innerText = '20'
    twenty.onclick = () => {
        entries = 20;
        recalculatePage();
    }
    entryDiv.appendChild(twenty)

    const fifty = document.createElement('button')
    fifty.innerText = '50'
    fifty.onclick = () => {
        entries = 50;
        recalculatePage();
    }
    entryDiv.appendChild(fifty)

    const ben = document.createElement('button')
    ben.innerText = '100'
    ben.onclick = () => {
        entries = 100;
        recalculatePage();
    }
    entryDiv.appendChild(ben)
}

export function recalculatePage(){
    const table = document.querySelector('.sortable-table');
    if(!table){return;}
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)
    let i=0;
    rowsArray.forEach((row, index) =>{
        let checkCells = filtered.filter(cell => (cell.row == index))
        let hidden = false
        checkCells.forEach((cell) => {
            if(cell.show == false){hidden = true}
        })
        if(hidden = false){i++}
    })
    max = i

    lastPage = Math.floor(max / entries) +1;
    if(page > lastPage){page = lastPage}
    showPage();
}
function showPage() {
    const table = document.querySelector('.sortable-table');
    if(!table){return;}
    const last = entries * page-1;
    const first = last - entries+1;
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)
    let i=0
    rowsArray.forEach((row, index) =>{
        let checkCells = filtered.filter(cell => (cell.row == index))
        let hidden = false
        checkCells.forEach((cell) => {
            if(cell.show == false){hidden = true}
        })
        if(hidden){ return; }

        if(first <= i && i <= last){
            row.style.display = ''
        }
        else{
            row.style.display = 'none'
        }
        i++
    })
    if(i != max){max=i}
    const tableNav = document.querySelector('.tableNav');
    const prevPage = tableNav.querySelector('.prevPage');
    const pageNo = tableNav.querySelector('.pageNo');
    const nextPage = tableNav.querySelector('.nextPage')
    prevPage.style.display = page==1 ? 'none' : '';
    nextPage.style.display = page==lastPage ? 'none' : '';

    const lastText = last > max ? max : last
    pageNo.innerText = `Page ${page} of ${lastPage} (Showing entries ${first+1}-${lastText} of ${max})`
}