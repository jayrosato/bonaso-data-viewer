import { addWarning, initWarning, clearWarning } from '../../../../static/js/customWarning.js'
document.addEventListener('DOMContentLoaded', async function () {
    const form = document.getElementById('response_form');

    const formID = document.getElementById('form_passer').getAttribute('form')

    async function loadLogic(){
        const response = await fetch(`/forms/data/query/forms/${formID}`)
        const formQuestions = await response.json()
        return formQuestions;
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
        updateForm(formQuestionInfo);
        verifyFields();
    });

    updateForm(formQuestionInfo);
    verifyFields();
});
const msg = document.getElementById('messages')

function verifyFields(){
    clearWarning();
    let msgs = []
    let flag = false
    const submitButton = document.getElementById('submitButton')
    //before performing any further validations
    const numbers = document.querySelectorAll('[number="yes"]')
    numbers.forEach((n) => {
        if(isNaN(parseInt(n.value)) && n.value != ''){
            flag = true
            msgs.push(`Confirm that numeric inputs are correct.`)
        }
    })
    const questions = document.querySelectorAll('div.form_question, input.form_question[type="text"]');
    questions.forEach((question, index) => {
        if(question.style.display == 'none'){
            question.removeAttribute('required');
            const inputs = question.querySelectorAll('input');
            inputs.forEach(input => input.removeAttribute('required'))
        }
        if(question.style.display != 'none'){
            if(question.nodeType == 'INPUT' && question.value == ''){
                flag = true;
                msgs.push(`You must answer question ${index + 1}`);
            }
            else{
                const inputs = question.querySelectorAll('input');
                const inputArray = Array.from(inputs)
                const anyFilled = inputArray.some(input => {
                    const checked = input.checked ? true : false;
                    return checked;
                })
                flag = anyFilled ? false : true
                if(flag){msgs.push( `You must answer question ${index + 1}`);}
            }
        }
    })
    if(flag){
        submitButton.setAttribute('type', 'button');
        submitButton.onclick = () => {
            initWarning()
            msgs.forEach(msg => addWarning(msg))
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
    const parentQuestion = document.querySelectorAll(`[fqid="${parentQuestionID}"]`);
    let actualValue = null;
    let none = false
    if(parentQuestion.length > 1){
        actualValue = []
        parentQuestion.forEach(pq => {
            if(pq.getAttribute('data-special') == 'None of the above' && pq.checked){
                none = true
            }
            const value = pq.checked ? pq.value : null
            if(value){actualValue.push(value)}
        })
    }
    else{
        console.log(rule.parent_question)
        actualValue = parentQuestion[0].value
    }

    if(actualValue == '' || actualValue == [] || none){
        return false;
    }
    const expectedValue = rule.expected_values;
    const limitOptions = rule.limit_options;
    const valueComparison = rule.value_comparison;
    const negate = rule.negate_value;
    if(Array.isArray(actualValue)){
        if(expectedValue == 'any' && actualValue.length > 0){
            return true;
        }
        let match = actualValue.includes(expectedValue) ? true : false;
        match = negate ? !match : match
        return match;
    }
    if(valueComparison == 'MATCHES' || valueComparison == 'EQUAL TO'){
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

function goLimitOptions(question, rule){
    const parentQuestionID = rule.parent_question;
    const parentQuestion = document.querySelectorAll(`[fqid="${parentQuestionID}"]`);
    let selectAll = false
    let checkedValues = []
    parentQuestion.forEach((input) => {
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
    if(!fqInfo){
        console.warn('This is unexpected. No logic was passed. Please try reloading the page.')
        return;
    }
    const questions = document.querySelectorAll('div.form_question, input.form_question[type="text"]');
    questions.forEach((question, index) => {
        let showValue = false
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
        let limitOptions = []
        if(operator == 'AND'){
            showValue = logic.rules.every((rule) => {
                const checkValue = checkQuestion(rule)
                if(rule.limit_options){
                    limitOptions.push({'question': question, 'rule':rule})
                }
                return checkValue;
            });
        }
        else if(operator == 'OR'){
            showValue = logic.rules.some(rule => {
                const checkValue = checkQuestion(rule)
                if(rule.limit_options){
                    goLimitOptions(question);
                }
                return checkValue;
            })
        }

        if(showValue){
            question.style.display = ''
            label.style.display = ''
        }
        if(!showValue){
            question.style.display = 'none'
            label.style.display = 'none'
            if(question.nodeName == 'INPUT'){
                question.value = '';
            }
            else{
                question.querySelectorAll('input[type=checkbox]').forEach(option => {option.checked = false});
                question.querySelectorAll('input[type=radio]').forEach(option => {option.checked = false});
            }
            
        }
        if(showValue && limitOptions.length > 0){
            limitOptions.forEach(element => {
                goLimitOptions(element.question, element.rule);
            })
        }

    })
}