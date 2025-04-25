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

const csrftoken = getCookie('csrftoken');

const div = document.querySelector('.content');
const submitButton = document.getElementById('submit');
const url = submitButton.getAttribute('submit-url')
submitButton.onclick = () => submit();

window.onload = loadExisting()

function loadExisting(){
    const existingOptions = document.getElementsByClassName('option_passer')
    Array.from(existingOptions).forEach((o) =>{
        let option = o.getAttribute('option_text')
        addOption(option)
    })
}


document.addEventListener('DOMContentLoaded', function () {
    const qTypeSelector = document.getElementById('id_question_type');

    qTypeSelector.addEventListener('change', function () {
        showOptions();
    });
});


function addOption(prefill=''){
    const optionDiv = document.createElement('div');
    optionDiv.setAttribute('class', 'option');
    const optionTextInput = document.createElement('input');
    optionTextInput.setAttribute('name', 'option_text');
    optionTextInput.setAttribute('type', 'text');
    optionTextInput.value = prefill
    optionDiv.appendChild(optionTextInput);

    const removeOptionButton = document.createElement('button');
    removeOptionButton.innerText = 'Remove Option';
    removeOptionButton.onclick = () => div.removeChild(optionDiv);
    optionDiv.appendChild(removeOptionButton);
    div.appendChild(optionDiv);


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
    const qText = document.getElementById('id_question_text').value;
    const qType = document.getElementById('id_question_type').value;
    const optionsInput = document.getElementsByName('option_text');
    const options = []
    Array.from(optionsInput).forEach((o) => {options.push(o.value)})
    console.log(qText, qType, options)

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
