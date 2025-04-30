document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('response_form');

    form.addEventListener('change', function () {
        updateForm();
        verifyFields();
    });

    updateForm(); // Run once on page load
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
function updateForm(){
    const questions = document.querySelectorAll('div.form_question, input.form_question[type="text"], input.form_question[type="number"]');
    for(let i = 0; i < questions.length; i++){
        let question = questions[i];

        if(question.nodeName.toLowerCase() == 'div'){
            const questionDependency = question.querySelectorAll('[questionRelation]')[0];
            if(questionDependency){
                const qdValue = questionDependency.getAttribute('questionRelation')
                const vdValue = questionDependency.getAttribute('valueRelation')
                const label = question.previousElementSibling
                const dependency = document.getElementsByName(qdValue);
                let matched = false; // Assume not matched at first

                for (let k = 0; k < dependency.length; k++) {
                    let item = dependency[k];
                    if (item && item.checked && item.value == vdValue) {
                        matched = true;
                        break; // Found a match, no need to continue
                    }
                }
                if (matched) {
                    question.style.display = '';
                    label.style.display = '';
                    const inputs = question.querySelectorAll('input')
                    for(let i=0; i< inputs.length; i++){
                        let type = inputs[i].getAttribute('type')
                        if(type == 'checkbox' || type =='radio'){
                            if(inputs[i].checked){
                                flagged = false
                                msg=''
                                break
                            }
                            flagged = true
                            msg = label.textContent
                        }
                    }
                } 
                else {
                    question.style.display = 'none';
                    label.style.display = 'none';
                    question.querySelectorAll('input[type=checkbox]').forEach(option => {option.checked = false});
                    question.querySelectorAll('input[type=radio]').forEach(option => {option.checked = false});
                }
            }
        }
        else{
            let questionDependency = question.getAttribute('questionRelation')
            let valueDependency = question.getAttribute('valueRelation')
            if(questionDependency){
                const id = question.getAttribute('id')
                const questionLabel = document.querySelector(`label[for="${id}"]`)

                const dependency = document.getElementsByName(questionDependency);
                let matched = false; // Assume not matched at first

                for (let k = 0; k < dependency.length; k++) {
                    let item = dependency[k];
                    if (item && item.checked && item.value == valueDependency) {
                        matched = true;
                        break; // Found a match, no need to continue
                    }
                }
                if (matched) {
                    questionLabel.style.display = '';
                    question.style.display = '';
                    if(question.value == ''){
                        flagged = true
                        msg = question.getAttribute('name')
                        break
                    }
                    flagged = false
                    msg=''
                } 
                else {
                    questionLabel.style.display = 'none';
                    question.style.display = 'none';
                    question.value = ''
                }
                
            }

        }
    }
}