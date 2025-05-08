window.onload = () => addClickable()

function addClickable(){
    let table = document.querySelector('.sortable-table');
    if(!table){
        return
    }
    headerTracker = []
    const headers = table.querySelectorAll('th')
    headers.forEach((h, index) => {
        headerTracker.push({h:true})
        h.onclick = () => {
            let sortDir = headerTracker[index]
            headerTracker[index] = !sortDir
            sortTable(index, sortDir)
        }
    })
}

function sortTable(index, asc=true){
    let table = document.querySelector('.sortable-table');
    const tableBody = table.tBodies[0]
    const rowsArray = Array.from(tableBody.rows)

    rowsArray.sort((current, next) => {
        const currentVal = current.cells[index].textContent.trim().toLowerCase()
        const nextVal = next.cells[index].textContent.trim().toLowerCase()
        if(currentVal < nextVal) return asc ? -1:1;
        if(currentVal > nextVal) return asc ? 1:-1;
        return 0
    });
    rowsArray.forEach(row => tableBody.appendChild(row));

    const headers = table.querySelectorAll('th');
    let header = headers[index];
    header.textContent = header.textContent.replace('↑', '').replace('↓', '');
    header.textContent += asc ? '↑' : '↓';
}