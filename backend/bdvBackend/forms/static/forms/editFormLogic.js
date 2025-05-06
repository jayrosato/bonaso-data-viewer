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
const questions = document.getElementsByClassName('question')

const msg = document.getElementById('msg')

function createButtons(q){
    const buttons = document.createElement('div')
    buttons.setAttribute('class', 'buttons')
    q.appendChild(buttons)

    const addQuestionButton = document.createElement('button');
    addQuestionButton.innerText = 'Add Question Below';
    addQuestionButton.type = ('button');
    addQuestionButton.onclick = () => addQuestion(q);
    buttons.appendChild(addQuestionButton);

    const addQuestionLogicButton = document.createElement('button');
    addQuestionLogicButton.innerText = 'Add Question Logic'
    addQuestionLogicButton.setAttribute('class', 'addQlButton')
    addQuestionLogicButton.type = ('button');
    addQuestionLogicButton.onclick = () => addQuestionLogic(q);
    buttons.appendChild(addQuestionLogicButton)

    const shiftQUpButton = document.createElement('button');
    shiftQUpButton.innerText = 'Move Question Up';
    shiftQUpButton.setAttribute('type', 'button');
    shiftQUpButton.onclick = () => shiftQUp(q);
    buttons.appendChild(shiftQUpButton);

    const shiftQDownButton = document.createElement('button');
    shiftQDownButton.innerText = 'Move Question Down';
    shiftQDownButton.setAttribute('type', 'button');
    shiftQDownButton.onclick = () => shiftQDown(q);
    buttons.appendChild(shiftQDownButton);

    const removeQuestionButton = document.createElement('button');
    removeQuestionButton.innerText = 'Remove Question';
    removeQuestionButton.type = ('button');
    removeQuestionButton.onclick = () => removeQuestion(q);
    buttons.appendChild(removeQuestionButton);
}

async function addQuestionLogic(q, existing=null){
    const ruleId = q.getAttribute('id')
    const cqId = q.getAttribute('id')
    const logicDiv = document.createElement('div')
    logicDiv.setAttribute('class', 'question-logic')
    logicDiv.setAttribute('id', `${cqId}-logic`)
    q.appendChild(logicDiv)

    const qlButton = q.querySelector('.addQlButton')
    qlButton.onclick = () => {
        q.removeChild(logicDiv)
        qlButton.innerText = 'Add Question Logic'
        qlButton.onclick = () => addQuestionLogic(q)
    }
    qlButton.innerText = 'Remove Question Logic'

    //create element allowing user to choose what happens when conditions are met
    const onMatchLabel = document.createElement('label')
    onMatchLabel.innerText = 'Show or hide on match?'
    logicDiv.appendChild(onMatchLabel)
    const onMatch = document.createElement('select')
    onMatch.setAttribute('name', `logic[${ruleId}][on_match]`)
    const onMatchShow = document.createElement('option')
    onMatchShow.innerText = 'Show'
    onMatchShow.value = 'Show'
    onMatch.appendChild(onMatchShow)
    const onMatchHide = document.createElement('option')
    onMatchHide.innerText = 'Hide'
    onMatchHide.value = 'Hide'
    onMatch.appendChild(onMatchHide)
    logicDiv.appendChild(onMatch)
    if(existing){
        onMatch.value = existing.on_match
    }

    const operatorLabel = document.createElement('label')
    operatorLabel.innerText = 'Operator (if dependent on multiple questions)'
    logicDiv.appendChild(operatorLabel)
    const operator = document.createElement('select')
    operator.setAttribute('name', `logic[${ruleId}][operator]`)
    const operatorAnd = document.createElement('option')
    operatorAnd.innerText = 'AND'
    operatorAnd.value = 'AND'
    operator.appendChild(operatorAnd)
    const operatorOr = document.createElement('option')
    operatorOr.innerText = 'OR'
    operatorOr.value = 'OR'
    operator.appendChild(operatorOr)
    logicDiv.appendChild(operator)
    if(existing){
        operator.value = existing.conditional_operator
    }

    const limitOptionsDiv = document.createElement('div')
    limitOptionsDiv.setAttribute('class', 'limit-options')
    logicDiv.appendChild(limitOptionsDiv)
    const limitOptionsLabel = document.createElement('label')
    limitOptionsLabel.innerText = 'Show options depending on parent Question?'
    const limitOptions = document.createElement('input')
    limitOptions.setAttribute('name', `logic[${ruleId}][limit_options]`)
    limitOptions.setAttribute('type', 'checkbox')
    limitOptionsDiv.appendChild(limitOptionsLabel)
    limitOptionsDiv.appendChild(limitOptions)
    if(existing){
        if(existing.limit_options == true)
            limitOptions.checked = true
    }

    const addRuleButton = document.createElement('button')
    addRuleButton.setAttribute('type', 'button')
    addRuleButton.onclick = () => newLogicRule(q, logicDiv, addRuleButton)
    addRuleButton.innerText = 'Add Another Rule'
    logicDiv.appendChild(addRuleButton)
    if(!existing){
        newLogicRule(q, logicDiv, addRuleButton)
    }
    if(existing){
        existing.rules[0].parent_question.forEach((rule, index)=>newLogicRule(q, logicDiv, addRuleButton, existing, index))
    }   
}

function newLogicRule(q, logicDiv, addRuleButton, existing=null, existingIndex=null){
    //create the question selector for a new rule
    const ruleId = q.getAttribute('id')

    const logicRule = document.createElement('div')
    logicRule.setAttribute('class', 'logicRule')
    logicDiv.insertBefore(logicRule, addRuleButton)
    const pqSelect = document.createElement('select')
    pqSelect.setAttribute('name', `logic[${ruleId}][parent_question]`)
    const parentQs = document.querySelectorAll('.question')
    const pqNull = document.createElement('option')
    pqNull.text = '-----'
    pqSelect.appendChild(pqNull)
    parentQs.forEach((pq) => {
        if(parseInt(q.getAttribute('id').split('-')[1]) > parseInt(pq.getAttribute('id').split('-')[1])){
            const selector = pq.querySelector('select')
            const questionId = selector.value
            const questionText = selector.options[selector.selectedIndex].text
            const pqOption = document.createElement('option')
            pqOption.value = questionId
            pqOption.text = questionText
            pqSelect.appendChild(pqOption)
        }
    })
    logicRule.appendChild(pqSelect)
    pqSelect.onchange = async() => {await setQLogicOptions(pqSelect, logicRule, ruleId)}
    if(existing){
        pqSelect.value = existing.rules[0].parent_question[existingIndex]
    }

    const negateDiv = document.createElement('div')
    negateDiv.setAttribute('class', 'negate')
    logicRule.appendChild(negateDiv)
    const negateLabel = document.createElement('label')
    negateLabel.innerText = 'If NOT:'
    const negate = document.createElement('input')
    negate.setAttribute('name', `logic[${ruleId}][negate_value]`)
    negate.setAttribute('type', 'checkbox')
    negateDiv.appendChild(negateLabel)
    negateDiv.appendChild(negate)
    if(existing){
        if(existing.rules[0].negate_value[existingIndex] == true){
            negate.checked = true
        }
    }

    const removeRuleButton = document.createElement('button')
    removeRuleButton.setAttribute('type', 'button')
    removeRuleButton.innerText='Remove Rule'
    removeRuleButton.onclick = () => logicDiv.removeChild(logicRule)
    logicRule.appendChild(removeRuleButton)
    console.log(existing)
    if(existing){
        existingValue = existing.rules[0].expected_values[existingIndex]
        setQLogicOptions(pqSelect, logicRule, ruleId, existingValue)
    }
}

async function setQLogicOptions(pqSelect, logicRule, ruleId, existingValue=null){   
    if(pqSelect.value == '-----'){
        return
    }
    const existingValueInput = logicRule.querySelector('#valueInput')
    if(existingValueInput){
        logicRule.removeChild(existingValueInput)
    }
    const qID = pqSelect.value
    const response = await fetch(`/forms/data/query/questions/${qID}/meta`)
    const options = await response.json()
    if(options.question_type == 'Single Selection' || options.question_type == 'Multiple Selections'){
        const valueInput = document.createElement('select')
        valueInput.setAttribute('id', 'valueInput')
        valueInput.setAttribute('name', `logic[${ruleId}][expected_values]`)
        options.option_ids.forEach((option, index) => {
            const poOption = document.createElement('option')
            poOption.value = option
            poOption.text = options.option_text[index]
            valueInput.appendChild(poOption)
            logicRule.appendChild(valueInput)
           if(existingValue){
                valueInput.value = existingValue
           }
        })
    }
    else if(options.question_type == 'Yes/No'){
        const valueInput = document.createElement('select')
        valueInput.setAttribute('name', `logic[${ruleId}][expected_values]`)
        
        const yesOption = document.createElement('option')
        yesOption.value = 'Yes'
        yesOption.innerText = 'Yes'
        valueInput.appendChild(yesOption)

        const noOption = document.createElement('option')
        noOption.value = 'No'
        noOption.innerText = 'No'
        valueInput.appendChild(noOption)

        logicRule.appendChild(valueInput)
        if(existingValue){
            valueInput.value = existingValue
        }
    }

    else if(options.question_type == 'Text'){
        const valueInput = document.createElement('input')
        valueInput.setAttribute('name', `logic[${ruleId}][expected_values]`)
        valueInput.setAttribute('type', 'text')
        logicRule.appendChild(valueInput)
        if(existingValue){
            valueInput.value = existingValue
        }
    }

    else if(options.question_type == 'Number'){
        const valueInput = document.createElement('input')
        valueInput.setAttribute('name', `logic[${ruleId}][expected_values]`)
        valueInput.setAttribute('type', 'number')
        logicRule.appendChild(valueInput)
        if(existingValue){
            valueInput.value = existingValue
        }
    }
}

async function checkLogic(q){
    const qIndex = parseInt(q.getAttribute('id').split('-')[1])-1
    const formID = document.getElementById('form-passer').getAttribute('form')
    const response = await fetch(`/forms/data/query/forms/questions/${formID}/${qIndex}`)
    const logic = await response.json()
    if(Object.keys(logic).length > 0){
        addQuestionLogic(q, logic)
    }
    
}
Array.from(questions).forEach((q) => {
    createButtons(q);
    checkLogic(q)
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

    /*
    //add checker for showing display if value here
    const qLogicSelect = questionDiv.querySelector('#id_visible_if_question')
    questionLogic(questionDiv)
    qLogicSelect.onchange = () => questionLogic(questionDiv)
    */

    //for the purpose of reorganzing quesitons, each question is marked with an id of 'question-id'
    //reset the index here
    const allQuestions =questionsList.children;
    for(let i=0; i<allQuestions.length; i++){
       allQuestions[i].setAttribute('id', `question-${i+1}`);
    };

    //set the class to be a new question. This is'nt important, but it just helps when inspecting the document
    questionDiv.setAttribute('class', 'question');

    //add the question to thequestionsList containing the other questions

    //this is a little annoying, but when cloning the previous questions, we also clone the buttons,
    //which will not work. So remove those now and then replace them with ones that will work.

    const oldButtons = questionDiv.querySelector('.buttons');
    oldButtons.remove()
    createButtons(questionDiv)
    
}

//function to remove a question. The question argument passed is thequestionsList that contains the button
//function also resets the index
//also protects against a user removing all questions, since that would mess up the crappy cloning system we came up with
function removeQuestion(question){
    if(questionsList.children.length == 1){
        msg.innerText = 'A form must have at least one question.'
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