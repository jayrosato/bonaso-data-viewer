import createFormQuestion from "./createFormQuestion.js";
import submitAsJson from "./submitAsJSON.js";
let csrftoken = null;

document.addEventListener('DOMContentLoaded', async function () {
    csrftoken = getCookie('csrftoken');
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
    let formID=null
    if(checkExisting){
        formID = checkExisting.getAttribute('form')
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
    else{
        createFormQuestion()
    }
    const content = document.querySelector('.content')
    const submitButton = document.createElement('button');
    submitButton.setAttribute('type', 'button');
    submitButton.innerText = 'Save Form';
    submitButton.onclick = () => submitAsJson(csrftoken, formID);
    content.appendChild(submitButton)
}

