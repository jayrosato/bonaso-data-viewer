document.addEventListener('DOMContentLoaded', async function () {
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

function checkInputs(amount, pqSelect, pqInput){
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
    }
    if(pqSelect.value == ''){
        amount.style.display = ''
    }
}

