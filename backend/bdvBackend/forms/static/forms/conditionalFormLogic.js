document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('new_response');

    form.addEventListener('change', function () {
        updateForm();
    });

    updateForm(); // Run once on page load
});

function updateForm(){
    console.log('updating')
    const questions = document.querySelectorAll('.question');
    for(let i=0; i< questions.length; i++){
        let question = questions[i]
        const questionDependency = question.getAttribute('questionRelation')
        const valueDependency = question.getAttribute('valueRelation')
        if(questionDependency){
            const dependency = document.getElementsByName(questionDependency)
            for(k=0; k < dependency.length; k++){
                let item=dependency[k]
                if(item){
                    let higherUp = question.parentElement.parentElement.parentElement.parentElement
                    if(item.checked){
                        if(item.value == valueDependency){
                            higherUp.style.visibility = 'visible'
                            break
                        }
                    }
                    else{
                        higherUp.style.visibility = 'hidden'
                        higherUp.querySelectorAll('input[type=checkbox]').forEach(option => {option.checked=false});
                        higherUp.querySelectorAll('input[type=radio]').forEach(option => {option.checked=false});
                    }
                }
            }
        }
    }
}
