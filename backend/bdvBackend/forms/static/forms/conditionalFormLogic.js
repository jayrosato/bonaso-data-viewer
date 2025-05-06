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

    form.addEventListener('change', function () {
        updateForm(questions, formLogic);
        verifyFields();
    });
    await loadLogic()
    updateForm(questions, formLogic); // Run once on page load
});

const submitButton = document.getElementById('submitButton')
let flagged = false
let msg = ''
function verifyFields(){
    if(flagged == true){
        submitButton.setAttribute('type', 'button')
        submitButton.onclick = () => document.getElementById('messages').innerText = `Please enter a response for question ${msg}`
    }
    else{
        submitButton.setAttribute('type', 'submit')
    }
}



//django forms load multiple choice options within a div, but not text choices, so we need to account for both

//uncheck
//negate
//limit options

function updateForm(questions, logic){
    for(let i = 0; i < questions.length; i++){
        let question = questions[i];
        let qLogic = logic.find(obj => obj['index'] === i)
        qLogic = qLogic['logic']
        //tracker variable to check if any rule is met
        let conditionMet = false
        let nextQuestion = false

        if(Object.keys(qLogic).length > 0){
            const pqs = []
            const operator = qLogic.conditional_operator

            const action = qLogic.on_match
            const limit_options = qLogic.limit_options
            const pqsIndex = qLogic.rules[0].parent_question_index
            const evs = qLogic.rules[0].expected_values
            const negate = qLogic.rules[0].negate_value
            pqsIndex.forEach((pqIndex) => {
                pq = questions[pqIndex]
                pqs.push(pq)
            })

            for(let q=0; q<pqs.length; q++){
                const pq = pqs[q]
                const ev = evs[q]
                if(pq.nodeName.toLowerCase() == 'div'){
                    const pqInputs = pq.querySelectorAll('input')
                    const values = []
                    pqInputs.forEach((i) => {
                        if(i.checked == true){
                            values.push(i.value)
                        }
                    })
                    if(values.includes(ev)){
                        conditionMet = true
                    }
                    else{
                        conditionMet = false
                        question.querySelectorAll('input[type=checkbox]').forEach(option => {option.checked = false});
                        question.querySelectorAll('input[type=radio]').forEach(option => {option.checked = false});
                    }
                }

                else{
                    let value = pq.value
                    if(value == ev){
                        conditionMet = true
                    }
                    else{
                        conditionMet = false
                        question.value = ''
                    }
                }

                if(operator == 'AND' && conditionMet == false){
                    question.style.display = 'none'
                    question.querySelectorAll('input[type=checkbox]').forEach(option => {option.checked = false});
                    question.querySelectorAll('input[type=radio]').forEach(option => {option.checked = false});
                    break
                }
                if(operator == 'OR' && conditionMet == true){
                    question.style.display = ''
                    break
                }
            }
            if(operator == 'OR' && conditionMet == false){
                question.style.display = 'none'
            }
            if(operator == 'AND' && conditionMet == true){
                question.style.display = ''
            }
        }
        //the question has no logic, and should be displayed at all times
        else{
            continue
        }
    }
}