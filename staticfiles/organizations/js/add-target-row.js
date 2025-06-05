import { addSearch } from "../../../../static/js/select-search.js";
import { checkInputs } from "./validate-targets.js";

document.addEventListener('DOMContentLoaded', async function () {
    const button = document.getElementById('add-row')
    button.onclick = () => addRow()
});

let index = 0
function addRow(){
    index ++
    const tbody = document.querySelector('tbody')
    const row = tbody.querySelector('tr')
    const newRow = row.cloneNode(true)
    const selects = newRow.querySelectorAll('select')
    selects.forEach(select => {
        select.value = ''
        if(select.getAttribute('id') == 'id_organization'){
            select.value = '1'
        }
    });
    const inputs = newRow.querySelectorAll('input')
    inputs.forEach(input => {
        input.value = '';
    });
    const searchBar = newRow.querySelectorAll('.selectSearch')
    if(searchBar){
        searchBar.forEach((bar) => {bar.remove()})
    }
    tbody.appendChild(newRow)

    //make sure that target-limit-option.js is in the tempalte
    const question = newRow.querySelector('#id_question')
    const option = newRow.querySelector('#id_match_option')
    question.onchange = () => updateOptions(question, option)

    //make sure that validate-targets.js is in the template
    const targetAmount = newRow.querySelector('#id_target_amount')
    const pqSelect = newRow.querySelector('#id_percentage_of_question')
    const pqInput = newRow.querySelector('#id_as_percentage')
    pqSelect.onchange = () => checkInputs(targetAmount, pqSelect, pqInput)
    targetAmount.onchange = () => checkInputs(targetAmount, pqSelect, pqInput)
    checkInputs(targetAmount, pqSelect, pqInput)

    //make sure that select-search.js is in the base html or the template, or this will throw an error
    addSearch()
}