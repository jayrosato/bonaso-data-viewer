import createSelect from '../../../../static/js/customSelector/create-select.js'
import { initWarning, addWarning, clearWarning } from '../../../../static/js/customWarning.js'

let csrftoken = null;
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

document.addEventListener('DOMContentLoaded', function () {
    csrftoken = getCookie('csrftoken')
    const qTypeSelector = document.getElementById('id_question_type');
    qTypeSelector.addEventListener('change', function () {
        showOptions();
    });
    showOptions();
});


const submitButton = document.getElementById('submit');
const submitRedirectButton = document.getElementById('submit-create');
const url = submitButton.getAttribute('submit-url')
submitButton.onclick = () => submit(false);
submitRedirectButton.onclick = () => submit(true);

function loadExisting(){
    const existingOptions = document.getElementsByClassName('option_passer')
    Array.from(existingOptions).forEach((o) =>{
        let option = o.getAttribute('option_text')
        let existingSpecial = o.getAttribute('special')
        addOption(option, existingSpecial)
    })
}

function addOption(existingText='', existingSpecial=null){
    const div = document.querySelector('.qForm');
    const optionDiv = document.createElement('div');
    optionDiv.setAttribute('class', 'option');
    const optionTextInput = document.createElement('input');
    optionTextInput.setAttribute('name', 'option_text');
    optionTextInput.setAttribute('type', 'text');
    optionTextInput.value = existingText
    optionDiv.appendChild(optionTextInput);

    const qTypeSelector = document.getElementById('id_question_type');
    const qType = qTypeSelector.value;
    if(qType == 'Multiple Selections'){
        const optionSpecialInput = createSelect(['None of the above', 'All'], null, true)
        optionSpecialInput.setAttribute('class', 'specialOption')
        optionDiv.appendChild(optionSpecialInput);
        Array.from(optionSpecialInput.options).forEach(option => {
            if (option.value == existingSpecial) {
                option.selected = true;
            }
        });
    }
    const removeOptionButton = document.createElement('button');
    removeOptionButton.innerText = 'Remove';
    removeOptionButton.onclick = () => div.removeChild(optionDiv);
    optionDiv.appendChild(removeOptionButton);
    div.insertBefore(optionDiv, addOptionButton)
}

function showOptions(){
    const div = document.querySelector('.qForm');
    const qTypeSelector = document.getElementById('id_question_type');
    const qType = qTypeSelector.value;
    if(qType == 'Single Selection' || qType == 'Multiple Selections'){
        if(!document.getElementById('addOptionButton')){
            const addOptionButton = document.createElement('button');
            addOptionButton.setAttribute('id', 'addOptionButton') ;
            addOptionButton.onclick = () => addOption();
            addOptionButton.innerText = 'Add an Option';
            div.appendChild(addOptionButton);
        };
        if(qType == 'Single Selection'){
            const specialSelect = document.querySelectorAll('.specialOption');
            specialSelect.forEach(special => special.remove())
        }
        if(qType == 'Multiple Selections'){
            const options = document.querySelectorAll('.option');
            options.forEach(option => {
                if(!option.querySelector('.specialOption')){
                    const optionSpecialInput = createSelect(['None of the above', 'All'], null, true)
                    optionSpecialInput.setAttribute('class', 'specialOption')
                    option.appendChild(optionSpecialInput);
                }
            })
        }
        loadExisting()
    }
    else{
        if(document.getElementById('addOptionButton')){
            div.removeChild(document.getElementById('addOptionButton'));
        }
        const options = document.getElementsByClassName('option');
        if(options.length > 0){
            Array.from(options).forEach((o) => {div.removeChild(o)});
        };
    };
};

async function submit(createAfter = false){
    let flag = false
    clearWarning();
    const qText = document.getElementById('id_question_text').value;
    if(qText.length > 255){
        addWarning('Question text must be less than 255 characters.')
        flag = true
    }
    if(qText == ''){
        addWarning('Question text cannot be blank.')
        flag = true
    }

    const qType = document.getElementById('id_question_type').value;
    if(qType == ''){
        addWarning('Please select a question type.')
        flag = true
    }

    const optionsInput = document.getElementsByName('option_text');
    const optionsSpecial = document.querySelectorAll('.specialOption');
    const options = []
    Array.from(optionsInput).forEach((o, index) => {
        if(o.value == ''){
            addWarning(`Option ${index + 1} cannot be blank!`)
            flag = true
        }
        else if(o.value.length > 255){
            addWarning(`Option ${index + 1} text must be less than 255 characters.`)
            flag = true
        }
        else{options.push({'text':o.value, 'special':optionsSpecial[index].value})}
    
    })
    if(flag == true){
        initWarning();
        return;
    }

    const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ question_text: qText,
                                question_type: qType,
                                options: options
                            }),
    });
    const responseJSON = await response.json();
    if(responseJSON.status == 'success'){
        const redirect = createAfter ? '/forms/questions/create' : '/forms/questions'
        console.log(redirect);
        window.location.href = redirect;
    }
};
