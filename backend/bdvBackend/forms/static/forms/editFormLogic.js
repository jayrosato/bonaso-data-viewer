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

const csrftoken = getCookie('csrftoken');

//question is thequestionsList that contains all of the form questions
const questionsList = document.querySelector('.questions');

//get the url for the question window
const url = questionsList.getAttribute('url')

//so that we can utilize Django forms (instead of building everything from scratch), html comes
//prepopualted with at least one instance of the form built in. 
//but for it to be usable, it needs buttons allowing a user to remove it or adjust its position,
//so add those buttons to each element that already exists (as indicated by it possessing the existing question class)
const questions = document.getElementsByClassName('existing-question')
Array.from(questions).forEach((q) => {
    const createQuestionButton = document.createElement('button');
    createQuestionButton.innerText = 'Create a new question';
    createQuestionButton.type = ('button');
    createQuestionButton.onclick = () => createQWindow(q);
    q.appendChild(createQuestionButton);

    const addQuestionButton = document.createElement('button');
    addQuestionButton.innerText = 'Add Question Below';
    addQuestionButton.type = ('button');
    addQuestionButton.onclick = () => addQuestion(q);
    q.appendChild(addQuestionButton);

    const removeQuestionButton = document.createElement('button');
    removeQuestionButton.innerText = 'Remove Question';
    removeQuestionButton.type = ('button');
    removeQuestionButton.onclick = () => removeQuestion(q);
    q.appendChild(removeQuestionButton);

    const shiftQUpButton = document.createElement('button');
    shiftQUpButton.innerText = 'Move Question Up';
    shiftQUpButton.setAttribute('type', 'button');
    shiftQUpButton.onclick = () => shiftQUp(q);
    q.appendChild(shiftQUpButton);

    const shiftQDownButton = document.createElement('button');
    shiftQDownButton.innerText = 'Move Question Down';
    shiftQDownButton.setAttribute('type', 'button');
    shiftQDownButton.onclick = () => shiftQDown(q);
    q.appendChild(shiftQDownButton);

})


//funciton to add a new quesiton by cloning a previous instance of a question
function addQuestion(question){
    //get the last existing question and clone it
    const questionDiv = question.cloneNode(true);

    //if this question had any values populated, set them to blank
    const emptyQ = questionDiv.querySelectorAll('option[value=""]');
    const selectedQ = questionDiv.querySelectorAll('option[selected=""]');
    for(let i=0; i<emptyQ.length; i++){
        if(emptyQ[i] != selectedQ[i]){
            selectedQ[i].removeAttribute('selected');
            emptyQ[i].setAttribute('selected', "");
        };
    };
    const textArea = questionDiv.querySelectorAll('textarea');
    for(let i=0; i<textArea.length; i++){
        textArea[i].value = '';
    }
    
    questionsList.insertBefore(questionDiv, question);
    question.after(questionDiv);

    //for the purpose of reorganzing quesitons, each question is marked with an id of 'question-id'
    //reset the index here
    const allQuestions =questionsList.children;
    for(let i=0; i<allQuestions.length; i++){
       allQuestions[i].setAttribute('id', `question-${i+1}`);
    };

    //set the class to be a new question. This is'nt important, but it just helps when inspecting the document
    questionDiv.setAttribute('class', 'new_question');

    //add the question to thequestionsList containing the other questions

    //this is a little annoying, but when cloning the previous questions, we also clone the buttons,
    //which will not work. So remove those now and then replace them with ones that will work.
    const buttons = questionDiv.querySelectorAll('button');
    buttons.forEach((b) => questionDiv.removeChild(b));

    //add the necessary buttons
    const createQuestionButton = document.createElement('button');
    createQuestionButton.innerText = 'Create a new question';
    createQuestionButton.type = ('button');
    createQuestionButton.onclick = () => createQWindow(questionDiv);
    questionDiv.appendChild(createQuestionButton);

    const addQuestionButton = document.createElement('button');
    addQuestionButton.innerText = 'Add Question Below';
    addQuestionButton.type = ('button');
    addQuestionButton.onclick = () => addQuestion(questionDiv);
    questionDiv.appendChild(addQuestionButton);

    const removeQuestionButton = document.createElement('button');
    removeQuestionButton.innerText = 'Remove Question';
    removeQuestionButton.setAttribute('type', 'button');
    removeQuestionButton.onclick = () => removeQuestion(questionDiv);
    questionDiv.appendChild(removeQuestionButton);

    const shiftQUpButton = document.createElement('button');
    shiftQUpButton.innerText = 'Move Question Up';
    shiftQUpButton.setAttribute('type', 'button');
    shiftQUpButton.onclick = () => shiftQUp(questionDiv);
    questionDiv.appendChild(shiftQUpButton);

    const shiftQDownButton = document.createElement('button');
    shiftQDownButton.innerText = 'Move Question Down';
    shiftQDownButton.setAttribute('type', 'button');
    shiftQDownButton.onclick = () => shiftQDown(questionDiv);
    questionDiv.appendChild(shiftQDownButton);
    
}

//function to remove a question. The question argument passed is thequestionsList that contains the button
//function also resets the index
//also protects against a user removing all questions, since that would mess up the crappy cloning system we came up with
function removeQuestion(question){
    if(questionsList.children.length == 1){
        console.log('A form must contain at least one question');
        return;
    };
   questionsList.removeChild(question);
    const allQuestions =questionsList.children;
    for(let i=0; i< allQuestions.length; i++){
       allQuestions[i].setAttribute('id', `question-${i+1}`);
    };
}

//function that places a question above another one in the questionquestionsList. Also switches its id
function shiftQUp(question){
    let index = question.getAttribute('id');
    index = index.split('-');
    index = index[1];
    index = parseInt(index);
    if(index==1){
        console.log('max uppage');
        return;
    }
    const target = document.getElementById(`question-${index-1}`);
    questionsList.insertBefore(question, target);
    target.setAttribute('id', 'question-');
    question.setAttribute('id', `question-${index-1}`);
    target.setAttribute('id', `question-${index}`);
}

//function that places a question beneath another one in the questionquestionsList. Also switches id.
function shiftQDown(question){
    let index = question.getAttribute('id');
    index = index.split('-');
    index = index[1];
    index = parseInt(index);

    if(index== questionsList.children.length){
        console.log('max downage');
        return;
    }
    const target = document.getElementById(`question-${index+1}`);
    questionsList.insertBefore(target, question);
    target.setAttribute('id', 'question-');
    question.setAttribute('id', `question-${index+1}`);
    target.setAttribute('id', `question-${index}`);
}

function createQWindow(question){
    const questionInput = question.querySelector('#id_question')
    const selectedQuestion = questionInput.value;
    if(selectedQuestion){
        window.open(`/forms/questions/${selectedQuestion}/update`)
    }
    else{
        window.open('/forms/questions/create')
    }
}