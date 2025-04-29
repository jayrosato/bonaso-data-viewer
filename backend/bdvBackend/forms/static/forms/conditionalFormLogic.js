document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('response_form');

    form.addEventListener('change', function () {
        updateForm();
    });

    updateForm(); // Run once on page load
});

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
                } 
                else {
                    question.style.display = 'none';
                    question.querySelectorAll('input[type=checkbox]').forEach(option => {option.checked = false});
                    question.querySelectorAll('input[type=radio]').forEach(option => {option.checked = false});
                    question.querySelectorAll('input[type=text]').forEach(option => {option.value = ''});
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