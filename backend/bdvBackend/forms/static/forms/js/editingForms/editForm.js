import createFormQuestion from "./createFormQuestion.js";
document.addEventListener('DOMContentLoaded', async function () {
    const csrftoken = getCookie('csrftoken');
    await buildForm();
});

//get cookie for csrf
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
};


async function buildForm(){
    const questions = document.querySelector('.questions')
    const checkExisting = document.querySelector('#form-passer')
    console.log(checkExisting)
    if(checkExisting){
        const formID = checkExisting.getAttribute('form')
        try{
            const response = await fetch(`/forms/data/query/forms/${formID}`)
            const formQuestions = await response.json()
            formQuestions.forEach(question => {
                createFormQuestion(question)
            });
        }
        catch(err){
            console.error('Could not get existing form information: ', err)
        }
    }
}

