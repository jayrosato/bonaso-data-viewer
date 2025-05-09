document.addEventListener('DOMContentLoaded', async function () {
    const form = document.getElementById('response_form');
    const questions = document.querySelectorAll('div.form_question, input.form_question[type="text"]');
    const formID = document.getElementById('form_passer').getAttribute('form')
    const formLogic = []
    async function loadLogic(){
        await Promise.all(
        Array.from(questions).map(async(question, index) => {
            const response = await fetch(`/forms/data/query/forms/questions/${formID}/${index}`)
            const logic = await response.json()
            formLogic.push({'index':index, 'logic':logic})
        })
        )
    }
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
    await loadLogic()
    updateForm(questions, formLogic); // Run once on page load
});

const submitButton = document.getElementById('submitButton')
let flags = []
let msg = ''
function verifyFields(){
    const numbers = document.querySelectorAll('[number="yes"]')
    numbers.forEach((n) => {
        if(isNaN(parseInt(n.value)) && n.value != ''){
            flags.push(n.getAttribute('name'))
        }
    })

    if(flags.length > 0){
        submitButton.setAttribute('type', 'button')
        let errorMsg = flags.join()
        submitButton.onclick = () => document.getElementById('messages').innerText += `Question(s) ${errorMsg} must be completed`
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

//negate

function updateForm(questions, logic){
    flags = []
    for(let i = 0; i < questions.length; i++){
        let question = questions[i];
        const label = question.previousElementSibling
        let qLogic = logic.find(obj => obj['index'] === i)
        qLogic = qLogic['logic']
        //tracker variable to check if any rule is met
        let conditionMet = false

        if(Object.keys(qLogic).length > 0){
            const pqs = []
            const operator = qLogic.conditional_operator
            const action = qLogic.on_match
            const limit_options = qLogic.limit_options
            const pqsIndex = qLogic.rules[0].parent_question_index
            const evs = qLogic.rules[0].expected_values
            const negate = qLogic.rules[0].negate_value
            const valueComp = qLogic.rules[0].value_comparison
            pqsIndex.forEach((pqIndex) => {
                pq = questions[pqIndex]
                pqs.push(pq)
            })
            for(let q=0; q<pqs.length; q++){
                const pq = pqs[q]
                const ev = evs[q]
                const vc = valueComp[q]
                const nv = negate[q]
                if(pq.nodeName.toLowerCase() == 'div'){
                    const pqInputs = pq.querySelectorAll('input')
                    let values = []
                    pqInputs.forEach((i) => {
                        if(i.checked == true){
                            if(i.getAttribute('data-special') == 'None of the above'){
                                values.push('nullify array')
                            }
                            values.push(i.value)
                        }
                    })
                    console.log(values)
                    if(values.includes('nullify array')){
                        values = []
                    }
                    if(ev == 'any' && values.length > 0){
                        conditionMet = true
                    }
                    else if(ev == 'none' && values.length == 0){
                        conditionMet = true
                    }
                    else if(nv==true && values.length>0 && !values.includes(ev)){
                        conditionMet = true
                    }
                    else if(values.includes(ev) && nv==false){
                        conditionMet = true
                    }
                    else{
                        conditionMet = false
                        question.querySelectorAll('input[type=checkbox]').forEach(option => {option.checked = false});
                        question.querySelectorAll('input[type=radio]').forEach(option => {option.checked = false});
                    }
                    if(limit_options){
                        let checkedValues = []
                        pqInputs.forEach((i) => {
                            if(i.checked == true){
                                checkedValues.push(i.parentElement.innerText.trim().toLowerCase())
                            }
                        })
                        question.querySelectorAll('input').forEach((q) =>{
                            if(!checkedValues.includes(q.parentElement.innerText.trim().toLowerCase()) && q.getAttribute('data-special') != 'None of the above'){
                                q.checked = false
                                q.parentElement.style.display = 'none'
                            }
                            else{
                                q.parentElement.style.display = ''
                            }
                        })
                    }
                }
                else{
                    let value = pq.value
                    let isNumber = pq.getAttribute('number')
                    if(isNumber == 'yes'){
                        value = parseInt(value)
                        if(isNaN(value)){
                            flags.push(question.getAttribute('id'))
                            console.log('warning, not a number')
                            conditionMet = false
                            continue
                        }
                    }
                    if(nv ==true && value != '' && value != ev){
                        conditionMet = true
                    }
                    else if(vc == 'CONTAINS' && value.includes(ev)){
                        conditionMet = true
                    }
                    else if(vc == 'DOES NOT CONTAIN' && !value.includes(ev) && value != ''){
                        conditionMet = true
                    }
                    else if(vc == 'GREATER THAN' && value > parseInt(ev)){
                        conditionMet = true
                    }
                    else if(vc == 'LESS THAN' && value < parseInt(ev)){
                        conditionMet = true
                    }
                    else if(value == ev && nv ==false){
                        conditionMet = true
                    }
                    else{
                        conditionMet = false
                        question.value = ''
                    }
                }
                if(conditionMet && question.nodeName.toLowerCase() === 'div') {
                    const inputs = question.querySelectorAll('input');
                    const type = inputs[0].getAttribute('type');
                
                    if (type === 'checkbox' || type === 'radio') {
                        let anyChecked = false;
                        for (let input of inputs) {
                            if (input.checked) {
                                anyChecked = true;
                                break;
                            }
                        }
                        const qid = question.getAttribute('id');
                
                        if(anyChecked) {
                            const index = flags.indexOf(qid);
                            if(index !== -1) {
                                flags.splice(index, 1)
                            }
                        } 
                        else {
                            if (!flags.includes(qid)) flags.push(qid);
                        }
                    }
                }
                else if (conditionMet) {
                    const qid = question.getAttribute('id');
                    console.log(flags)
                    if (question.value == '') {
                        if (!flags.includes(qid)){
                            flags.push(qid);
                        }
                    } 
                    else {
                        const index = flags.indexOf(qid);
                        if(index !== -1){
                            flags.splice(index, 1)
                        };
                    }
                }

                if(operator == 'AND' && conditionMet == false){
                    label.style.display = 'none'
                    question.style.display = 'none'
                    question.querySelectorAll('input[type=checkbox]').forEach(option => {option.checked = false});
                    question.querySelectorAll('input[type=radio]').forEach(option => {option.checked = false});
                    break
                }
                if(operator == 'OR' && conditionMet == true){
                    label.style.display = ''
                    question.style.display = ''
                    break
                }
            }
            if(conditionMet == true){
                label.style.display = ''
                question.style.display = ''
                conditionMet = true
            }
            else if(conditionMet == false){
                label.style.display = 'none'
                question.style.display = 'none'
            }
        }
        //the question has no logic, and should be displayed at all times
        else{
            continue
        }
    }
    document.querySelectorAll('input, select, textarea').forEach(element => {
        if (element.offsetParent === null) { // hidden element
            element.removeAttribute('required');
        }
    });
}