//global trackers to make pages easier to manage
let page = 1
let entries = 10
let lastPage = 1
let max = 0

import { addClickable, createFilters } from "./sort-filter-tables.js";
import { createButtons, showPage } from "./table-pages.js";
document.addEventListener('DOMContentLoaded', async function () {
    //prepare pages
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
    
    //run functions to add filter/sort icons
    addClickable()
    createFilters()
});