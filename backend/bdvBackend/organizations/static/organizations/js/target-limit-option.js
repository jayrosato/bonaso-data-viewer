document.addEventListener('DOMContentLoaded', async function () {
    const questions = document.querySelectorAll('#id_question')
    const optionSelect = document.querySelectorAll('#id_match_option')
    questions.forEach((question, index) => {
        question.onchange = () => updateOptions(question, optionSelect[index])
    })
});

async function updateOptions(question, optionSelect){
    const qID = question.value
    if(qID){
        const response = await fetch(`/forms/data/query/questions/${qID}/meta`)
        const optionsInfo = await response.json()
        const options = optionSelect.querySelectorAll('option')
        if(optionsInfo.question_type == 'Single Select' || optionsInfo.question_type == 'Multiple Selections'){
            options.forEach((option) => {
                if(optionsInfo.option_ids.includes(parseInt(option.value))){
                    option.style.display = ''
                }
                else{
                    option.style.display = 'none'
                }
            })
        }
    }
}