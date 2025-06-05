import { addWarning, initWarning, clearWarning } from '../../../../static/js/customWarning.js';

document.addEventListener('DOMContentLoaded', async function () {
    const form = document.querySelector('#target-form')
    form.addEventListener('change', function () {validateTargets()})
    const numberInputs = document.querySelectorAll('#id_target_amount')
    const pqSelects = document.querySelectorAll('#id_percentage_of_question')
    const pqInputs = document.querySelectorAll('#id_as_percentage')

    numberInputs.forEach((input, index) => {
        input.onchange = () => checkInputs(numberInputs[index], pqSelects[index], pqInputs[index])
    })
    pqSelects.forEach((input, index) => {
        input.onchange = () => checkInputs(numberInputs[index], pqSelects[index], pqInputs[index])
})
});

function validateTargets(){
    let messages = [];
    console.log('validating');
    clearWarning();
    let flagged = false
    const submit = document.getElementById('submit')
    const table = document.querySelector('tbody')
    let amounts = null
    let pqSelects = null
    let pqInputs = null
    if(table){
        amounts = table.querySelectorAll('#id_target_amount')
        pqSelects = table.querySelectorAll('#id_percentage_of_question')
        pqInputs = table.querySelectorAll('#id_as_percentage')
    }
    else{
        amounts = document.querySelectorAll('#id_target_amount')
        pqSelects = document.querySelectorAll('#id_percentage_of_question')
        pqInputs = document.querySelectorAll('#id_as_percentage') 
    }
    amounts.forEach((amount, index) => {
        const amountValue = amount.value
        const pqSelectValue = pqSelects[index].value
        const pqInputsValue = pqInputs[index].value
        console.log(amountValue, pqSelectValue)
        if(amountValue == '' && pqSelectValue == ''){

            messages.push(`Target in row ${index+1} must have either a target amount or a percentage of a question.`)
            flagged = true
        }
        else if(pqInputsValue == '' && pqSelectValue != ''){
            messages.push(`Target in row ${index+1} must have percent.`)
            flagged = true
        }
        else if(pqInputsValue < 0 || pqInputsValue > 100){
            messages.push(`Percent in row ${index+1} must be between 1 and 100%.`)
            flagged = true
        }
    })
    if(flagged){
        submit.setAttribute('type', 'button')
        submit.onclick = () => {
            messages.forEach(msg => addWarning(msg));
            initWarning();
        }
    }
    else if(!flagged){
        submit.setAttribute('type', 'submit')
    }
}

export function checkInputs(amount, pqSelect, pqInput){
    if(amount.value != ''){
        pqSelect.style.display = 'none'
        pqInput.style.display = 'none'
        pqSelect.value = ''
        pqInput.value = ''
    }
    if(amount.value == ''){
        pqSelect.style.display = ''
        pqInput.style.display = ''
    }
    if(pqSelect.value != ''){
        amount.style.display = 'none'
        amount.value = ''
        if(pqInput.value == ''){
            pqInput.value = 100
        }
    }
    if(pqSelect.value == ''){
        amount.style.display = ''
    }
}

