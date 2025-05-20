document.addEventListener('DOMContentLoaded', async function () {
    const form = document.getElementById('response_form');

    const formID = document.getElementById('form_passer').getAttribute('form')
    const formLogic = []
    async function loadLogic(){
        const response = await fetch(`/forms/data/query/forms/${formID}`)
        const formQuestions = await response.json()
        return formQuestions.form_questions;
    }
    const formQuestionInfo = await loadLogic()

    function loadSpecialOptions(){
        const msInputs = document.querySelectorAll('[data-special]')
        msInputs.forEach((input) => {
            input.onclick = () => manageSpecialOptions(input)
        })
    }
    loadSpecialOptions()

    form.addEventListener('change', function () {
        updateForm(questions, formLogic);
        verifyFields();
    });

    updateForm(formQuestionInfo); // Run once on page load
});

let flag = false
let errorMsg = ''
function verifyFields(){
    const submitButton = document.getElementById('submitButton')
    const msg = document.getElementById('messages')

    //before performing any further validations
    const numbers = document.querySelectorAll('[number="yes"]')
    numbers.forEach((n) => {
        if(isNaN(parseInt(n.value)) && n.value != ''){
            flag = true
            errorMsg += `\nConfirm that numeric inputs are correct.`
        }
    })
    if(flag){
        submitButton.setAttribute('type', 'button');
        submitButton.onclick = () => {
            msg.innerText = errorMsg;
            errorMsg = ''
        }
    }
    else{
        submitButton.setAttribute('type', 'submit')
    }
}

function manageSpecialOptions(input){
    const question = input.parentElement.parentElement.parentElement
    const options = question.querySelectorAll('[data-special]')
    const special = input.getAttribute('data-special')
    if(special == 'None of the above' || special == 'All'){
        options.forEach((option) => {
            if(option != input){
                option.checked = false
            }
        })
    }
    else{
        options.forEach((option) => {
            let spec = option.getAttribute('data-special')
            if(spec == 'None of the above' || spec == 'All'){
                option.checked = false
            }
        })
    }
}   

//django forms load multiple choice options within a div, but not text choices, so we need to account for both


function checkQuestion(rule){
    const parentQuestionID = rule.parent_question;
    const parentQuestion = document.querySelector(`[fqid="${parentQuestionID}"]`);
    const actualValue = parentQuestion.value
    if(actualValue == ''){
        return false;
    }
    const expectedValue = rule.expected_values;
    const limitOptions = rule.limit_options;
    const valueComparison = rule.value_comparison;
    const negate = rule.negate_value;
    if(!valueComparison || valueComparison == 'MATCHES' || valueComparison == 'EQUAL TO'){
        let match = expectedValue == actualValue ? true : false;
        match = negate ? !match : match
        return match;
    }
    if(valueComparison == 'GREATER THAN'){
        const match = expectedValue < actualValue ? true : false;
        return match;
    }
    if(valueComparison == 'LESS THAN'){
        const match = expectedValue > actualValue ? true : false;
        return match;
    }
    if(valueComparison == 'CONTAINS'){
        const match = actualValue.includes(expectedValue) ? true : false;
        return match;
    }
    if(valueComparison == 'DOES NOT CONTAIN'){
        const match = actualValue.includes(expectedValue) ? false : true;
        return match;
    }
}

function goLimitOptions(question, parentQuestionInputs){
    let selectAll = false
    let checkedValues = []
    parentQuestionInputs.forEach((input) => {
        if(input.checked == true){
            if(input.getAttribute('data-special') == 'All'){
                selectAll = true;
            }
            checkedValues.push(input.parentElement.innerText.trim().toLowerCase())
        }
    })
    question.querySelectorAll('input').forEach((q) =>{
        if(!checkedValues.includes(q.parentElement.innerText.trim().toLowerCase()) && q.getAttribute('data-special') != 'None of the above' && !selectAll){
            q.checked = false
            q.parentElement.style.display = 'none'
        }
        else{
            q.parentElement.style.display = ''
        }
    })
}

function updateForm(fqInfo){
    flag = false;
    const questions = document.querySelectorAll('div.form_question, input.form_question[type="text"]');
    questions.forEach((question, index) => {
        const label = question.previousElementSibling;
        //assuming this works since both of these are ordered by index in their respective views
        const info = fqInfo[index];
        if(!info.logic){ 
            return; 
        }
        if(!info.logic.rules || info.logic.rules.length == 0){
            return;
        }
        const logic = info.logic;
        const operator = logic.conditional_operator;
        if(operator == 'AND'){
            logic.rules.every((rule) => {
                const showValue = checkQuestion(rule)
            });
        }
        else if(operator == 'OR'){
            logic.rules.some(rule => {
                const showValue = checkQuestion(rule)
            })
        }
        if(showValue){
            question.style.display = ''
            label.style.display = ''
            //figure out how to get this
            if(limitOptions){
                parentQuestionInputs = parentQuestion.getAllInputs()
                goLimitOptions(question)
            }
        }
        if(!showValue){
            question.style.display = 'none'
            label.style.display = 'none'
        }

    })
}