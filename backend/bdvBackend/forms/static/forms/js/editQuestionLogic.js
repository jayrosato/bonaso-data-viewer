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

let csrftoken = null;

const div = document.querySelector('.qForm');
const submitButton = document.getElementById('submit');
const url = submitButton.getAttribute('submit-url')
submitButton.onclick = () => submit();
const warnings = document.getElementById('warnings')

document.addEventListener('DOMContentLoaded', function () {
    csrftoken = getCookie('csrftoken')
    const qTypeSelector = document.getElementById('id_question_type');
    qTypeSelector.addEventListener('change', function () {
        showOptions();
    });
    showOptions();
});

//pre pop special stuff here!
function loadExisting(){
    const existingOptions = document.getElementsByClassName('option_passer')
    Array.from(existingOptions).forEach((o) =>{
        let option = o.getAttribute('option_text')
        let existingSpecial = o.getAttribute('special')
        addOption(option, existingSpecial)
    })
}

function addOption(existingText='', existingSpecial=''){
    const optionDiv = document.createElement('div');
    optionDiv.setAttribute('class', 'option');
    const optionTextInput = document.createElement('input');
    optionTextInput.setAttribute('name', 'option_text');
    optionTextInput.setAttribute('type', 'text');
    optionTextInput.value = existingText
    optionDiv.appendChild(optionTextInput);

    const optionSpecialInput = document.createElement('select')
    optionSpecialInput.setAttribute('name', 'special')
    optionSpecialInput.setAttribute('search', 'no')
    const specialShow = ['-----', 'None of the above', 'All'] //should probably add an all here
    const special = ['', 'None of the above', 'All']
    special.forEach((val, index) => {
        const option = document.createElement('option')
        option.setAttribute('value', val)
        option.innerText = specialShow[index]
        optionSpecialInput.appendChild(option)
    })
    optionDiv.appendChild(optionSpecialInput)
    Array.from(optionSpecialInput.options).forEach(option => {
        if (option.value === existingSpecial) {
            option.selected = true;
        }
    });

    const removeOptionButton = document.createElement('button');
    removeOptionButton.innerText = 'Remove Option';
    removeOptionButton.onclick = () => div.removeChild(optionDiv);
    optionDiv.appendChild(removeOptionButton);
    div.insertBefore(optionDiv, addOptionButton)
    //div.appendChild(optionDiv);
}

function showOptions(){
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

function submit(){
    let flag = false
    const qText = document.getElementById('id_question_text').value;
    if(qText.length > 255){
        warnings.innerText += ' Question text must be less than 255 characters.'
        flag = true
    }
    if(qText == ''){
        warnings.innerText += ' Question text cannot be blank.'
        flag = true
    }

    const qType = document.getElementById('id_question_type').value;
    if(qType == ''){
        warnings.innerText += ' Please select a question type.'
        flag = true
    }

    const optionsInput = document.getElementsByName('option_text');
    const optionsSpecial = document.getElementsByName('special');
    const options = []
    Array.from(optionsInput).forEach((o, index) => {
        if(o.value == ''){
            warnings.innerText += ' Option cannot be blank'
            flag = true
        }
        else if(o.value.length > 255){
            warnings.innerText += ' Option must be less than 255 characters.'
            flag = true
        }
        else{options.push({'text':o.value, 'special':optionsSpecial[index].value})}
    
    })
    if(flag == true){
        return
    }

    fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ question_text: qText,
                                question_type: qType,
                                options: options
                            }),
      })
      .then(response => response.json())
      .then(result => {
        if (result.redirect) {
            window.location.href = result.redirect;
        } else {
            console.log('Data was logged, but the redirect failed. You can safely leave this page.');
        }
    });
};
