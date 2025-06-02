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
    let index = q.getAttribute('index');
    index = parseInt(index);
    if(index == 0){
        addQuestionLogicButton.onclick = () => msg.innerText = 'The first question of a form must always be shown, and therefore cannot have logic.'
        addQuestionLogicButton.style.backgroundColor = 'grey'
    }
    else{
        addQuestionLogicButton.onclick = () => addQuestionLogic(q);
        buttons.appendChild(addQuestionLogicButton)
    }
    buttons.append(addQuestionLogicButton)

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
    const ruleId = q.getAttribute('index')
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

    //create element allowing user to choose what happens when conditions are met (debating to keep this feature)
    /*
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
    //onMatch.appendChild(onMatchHide)
    logicDiv.appendChild(onMatch)
    if(existing){
        onMatch.value = existing.on_match
    }
    */

    const onMatchLabel = document.createElement('label')
    onMatchLabel.innerText = 'Show when: '
    onMatchLabel.style.fontWeight = 'bold'
    logicDiv.appendChild(onMatchLabel)

    const operatorLabel = document.createElement('label')
    operatorLabel.innerText = 'Operator (if dependent on multiple questions)'
    logicDiv.appendChild(operatorLabel)
    const operator = document.createElement('select')

    operator.setAttribute('name', `logic[${ruleId}][operator]`)
    operator.setAttribute('search', 'no')
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
    else{
        operator.value = 'AND'
    }

    //hide these by default, since they are meaningless if there is only one rule
    operatorLabel.display = 'none';
    operator.style.display = 'none';

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
    const ruleId = q.getAttribute('index')

    const logicRule = document.createElement('div')
    logicRule.setAttribute('class', 'logic-rule')
    logicDiv.insertBefore(logicRule, addRuleButton)

    const ruleHeader = document.createElement('h4')
    ruleHeader.innerText = 'Rule:'
    logicRule.appendChild(ruleHeader)

    const removeRuleButton = document.createElement('button')
    removeRuleButton.setAttribute('type', 'button')
    removeRuleButton.innerText='Remove Rule'
    removeRuleButton.onclick = () => {
        logicDiv.removeChild(logicRule)
        const checkRules = logicDiv.querySelectorAll('.logic-rule')
        if(checkRules && checkRules.length == 1){
            const operator = logicDiv.querySelector(`[name = "logic[${ruleId}][operator]"]`)
            operator.style.display = 'none'
        }
        if(checkRules.length == 0){
            q.removeChild(logicDiv)
            const addQlButton = q.querySelector('.addQlButton')
            addQlButton.innerText = 'Add Question Logic'
            addQlButton.onclick = () => addQuestionLogic(q)
        }
    }
    logicRule.appendChild(removeRuleButton)

    const questionHeader = document.createElement('p')
    questionHeader.innerText = 'When Question:'
    logicRule.appendChild(questionHeader)

    const pqSelect = document.createElement('select')
    pqSelect.setAttribute('name', `logic[${ruleId}][parent_question]`)
    pqSelect.setAttribute('class', 'pqSelect')
    const parentQs = document.querySelectorAll('.question')
    const pqNull = document.createElement('option')
    pqNull.text = '-----'
    pqSelect.appendChild(pqNull)
    parentQs.forEach((pq) => {
        if(parseInt(q.getAttribute('index')) > parseInt(pq.getAttribute('index'))){
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
    addSearch()
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

    const limitOptionsDiv = document.createElement('div')
    limitOptionsDiv.setAttribute('class', 'limit-options')
    logicRule.appendChild(limitOptionsDiv)
    const limitOptionsLabel = document.createElement('label')
    limitOptionsLabel.innerText = 'Limit Options based on Question'
    const limitOptions = document.createElement('input')
    limitOptions.setAttribute('name', `logic[${ruleId}][limit_options]`)
    limitOptions.setAttribute('type', 'checkbox')
    limitOptionsDiv.appendChild(limitOptionsLabel)
    limitOptionsDiv.appendChild(limitOptions)
    if(existing){
        if(existing.limit_options == true)
            limitOptions.checked = true
    }

    if(existing){
        existingValue = existing.rules[0].expected_values[existingIndex]
        setQLogicOptions(pqSelect, logicRule, ruleId, existingValue)
    }
    const checkRules = logicDiv.querySelectorAll('.logic-rule')
    if(checkRules && checkRules.length > 1){
        const operator = logicDiv.querySelector(`[name = "logic[${ruleId}][operator]"]`)
        operator.style.display = ''
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
    const existingCompareInput = logicRule.querySelector('#compareInput')
    if(existingCompareInput){
        logicRule.removeChild(existingCompareInput)
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
        })
        const anyOption = document.createElement('option')
        anyOption.value = 'any'
        anyOption.text = 'Anything Selected'
        valueInput.appendChild(anyOption)

        const noneOption = document.createElement('option')
        noneOption.value = 'none'
        noneOption.text = 'Nothing Selected'
        valueInput.appendChild(noneOption)

        logicRule.appendChild(valueInput)
        if(existingValue){
            valueInput.value = existingValue
        }
    }
    else if(options.question_type == 'Yes/No'){
        const valueInput = document.createElement('select')
        valueInput.setAttribute('id', 'valueInput')
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
        valueInput.setAttribute('id', 'valueInput')
        valueInput.setAttribute('name', `logic[${ruleId}][expected_values]`)
        valueInput.setAttribute('type', 'text')
        logicRule.appendChild(valueInput)
        if(existingValue){
            valueInput.value = existingValue
        }
        //set up comparison input
        const compareInput = document.createElement('select')
        compareInput.setAttribute('name', `logic[${ruleId}][value_comparison]`)
        compareInput.setAttribute('id', 'compareInput')
        const operatorMatch = document.createElement('option')
        operatorMatch.innerText = 'MATCHES'
        operatorMatch.value = 'MATCHES'
        compareInput.appendChild(operatorMatch)

        const operatorCont = document.createElement('option')
        operatorCont.innerText = 'CONTAINS'
        operatorCont.value = 'CONTAINS'
        compareInput.appendChild(operatorCont)

        const operatorDNC = document.createElement('option')
        operatorDNC.innerText = 'DOES NOT CONTAIN'
        operatorDNC.value = 'DOES NOT CONTAIN'
        compareInput.appendChild(operatorDNC)

        logicRule.appendChild(compareInput)
    }

    else if(options.question_type == 'Number'){
        const valueInput = document.createElement('input')
        valueInput.setAttribute('name', `logic[${ruleId}][expected_values]`)
        valueInput.setAttribute('id', 'valueInput')
        valueInput.setAttribute('type', 'number')
        logicRule.appendChild(valueInput)
        if(existingValue){
            valueInput.value = existingValue
        }

        //set up comparison input
        const compareInput = document.createElement('select')
        compareInput.setAttribute('name', `logic[${ruleId}][value_comparison]`)
        compareInput.setAttribute('id', 'compareInput')
        const operatorEqual = document.createElement('option')
        operatorEqual.innerText = 'EQUAL TO'
        operatorEqual.value = 'EQUAL TO'
        compareInput.appendChild(operatorEqual)

        const operatorGT = document.createElement('option')
        operatorGT.innerText = 'GREATER THAN'
        operatorGT.value = 'GREATER THAN'
        compareInput.appendChild(operatorGT)
    
        const operatorLT = document.createElement('option')
        operatorLT.innerText = 'LESS THAN'
        operatorLT.value = 'LESS THAN'
        compareInput.appendChild(operatorLT)

        logicRule.appendChild(compareInput)
    }
}

async function checkLogic(q){
    const qIndex = parseInt(q.getAttribute('index'))
    if(document.getElementById('form-passer')){
        const formID = document.getElementById('form-passer').getAttribute('form')
        const response = await fetch(`/forms/data/query/forms/questions/${formID}/${qIndex}`)
        const logic = await response.json()
        if(Object.keys(logic).length > 0){
            addQuestionLogic(q, logic)
        }
    }
}
function addQChangeEvent(q){
    const qSelect = q.querySelector('#id_question')
    qSelect.onchange = () => updateRules(q)
}

function updateRules(q){
    let index = q.getAttribute('index');
    index = parseInt(index);

    const pqSelects = document.querySelectorAll(`.pqSelect`)
    pqSelects.forEach(pqSelect =>{
        const pqSelectIndex = parseInt(pqSelect.parentElement.parentElement.parentElement.getAttribute('index'))
        if(pqSelectIndex <= index){
            return
        }
        const options = pqSelect.querySelectorAll('option')
        options.forEach(option => {
            if(option.value){
                pqSelect.removeChild(option)
            }
        })
        const parentQs = document.querySelectorAll('.question')
        parentQs.forEach((pq) => {
            if(pqSelectIndex > pq.getAttribute('index')){
                const selector = pq.querySelector('select')
                const questionId = selector.value
                const questionText = selector.options[selector.selectedIndex].text
                const pqOption = document.createElement('option')
                pqOption.value = questionId
                pqOption.text = questionText
                pqSelect.appendChild(pqOption)
            }
        })
    })
}
Array.from(questions).forEach((q) => {
    createButtons(q);
    addQChangeEvent(q);
    checkLogic(q)
})


//funciton to add a new quesiton by cloning a previous instance of a question
function addQuestion(question){
    //get the last existing question and clone it
    const questionDiv = question.cloneNode(true);

    //if this question had any values populated, set them to blank
    const questionSelect = questionDiv.querySelector('#id_question')
    questionSelect.value = ''
    //also, if a search bar was present, remove it
    const searchBar = questionDiv.querySelector('.select-search')
    if(searchBar){
        questionDiv.removeChild(searchBar)
    }
    

    //remove any logic as well
    if(questionDiv.querySelector('.question-logic')){
        const logic = questionDiv.querySelector('.question-logic')
        questionDiv.removeChild(logic)
    }
    
    questionsList.insertBefore(questionDiv, question);
    question.after(questionDiv);

    //for the purpose of reorganzing quesitons
    //reset the index here
    const allQuestions =questionsList.children;
    for(let i=0; i<allQuestions.length; i++){
       allQuestions[i].setAttribute('index', `${i}`);
    };

    //set the class to be a new question. This is'nt important, but it just helps when inspecting the document
    questionDiv.setAttribute('class', 'question');

    //add the question to thequestionsList containing the other questions

    //this is a little annoying, but when cloning the previous questions, we also clone the buttons,
    //which will not work. So remove those now and then replace them with ones that will work.
    const oldButtons = questionDiv.querySelector('.buttons');
    oldButtons.remove()
    createButtons(questionDiv)
    addSearch() //add search ability, make sure select-search is included in the base
    
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
        allQuestions[i].setAttribute('index', `${i}`);
        if(i==0){
            const qLogicButton = allQuestions[i].querySelector('.addQlButton')
            qLogicButton.onclick = () => msg.innerText = 'The first question of a form must always be shown, and therefore cannot have logic.'
            qLogicButton.style.backgroundColor = 'grey'
        }
        reorderLogic(allQuestions[i], i)
    };
    
}

//function that places a question above another one in the questionquestionsList. Also switches its id
function shiftQUp(question){
    let index = question.getAttribute('index');
    index = parseInt(index);
    const questionsList = document.querySelector('.questions');
    if(index==0){
        console.log('max uppage');
        return;
    }
    if(index == 1 && question.querySelector('.question-logic') != null){
        msg.innerText = 'The first question of a form cannot contain logic. Please remove logic from this question before moving it up.'
        return;
    }
    const target = document.querySelector(`[index="${index-1}"]`);
    questionsList.insertBefore(question, target);
    target.setAttribute('index', index);
    question.setAttribute('index', index-1);
    index = parseInt(question.getAttribute('index'))
    reorderLogic(question, index)
    reorderLogic(target, index+1)
    updateRules(question)
    console.log(index)
    if(index == 0){
        const qLogicButton = question.querySelector('.addQlButton')
        qLogicButton.onclick = () => msg.innerText = 'The first question of a form must always be shown, and therefore cannot have logic.'
        qLogicButton.style.backgroundColor = 'grey'

        const targetQLB = target.querySelector('.addQlButton')
        targetQLB.onclick = () => addQuestionLogic(question)
        targetQLB.style.backgroundColor = 'green'
    }
}

//function that places a question beneath another one in the questionquestionsList. Also switches id.
function shiftQDown(question){
    let index = question.getAttribute('index');
    index = parseInt(index);
    const questionsList = document.querySelector('.questions');
    if(index == questionsList.children.length-1){
        console.log('max downage');
        return;
    }
    const target = document.querySelector(`[index="${index+1}"]`);
    questionsList.insertBefore(target, question);
    question.setAttribute('index', index+1);
    target.setAttribute('index', index);
    index = parseInt(question.getAttribute('index'))
    reorderLogic(question, index)
    reorderLogic(target, index-1)
    updateRules(question)
    console.log(index)
    if(index ==1){
        const qLogicButton = question.querySelector('.addQlButton')
        qLogicButton.onclick = () => addQuestionLogic(question)
        qLogicButton.style.backgroundColor = 'green'

        const targetQLB = target.querySelector('.addQlButton')
        targetQLB.onclick = () => msg.innerText = 'The first question of a form must always be shown, and therefore cannot have logic.'
        targetQLB.style.backgroundColor = 'grey'
    }
}

function reorderLogic(question, index){
    const logic = question.querySelector('.question-logic')
    if(logic){
        const selects = logic.querySelectorAll('select')
        selects.forEach((select) => {
            let name = select.getAttribute('name')
            const regex = /logic\[\d+\]/
            const replace = name.match(regex)[0];
            const value = `logic[${index}]`
            newName = name.replace(replace, value)
            select.setAttribute('name', newName)
        })
        const inputs = logic.querySelectorAll('input')
        console.log(inputs)
        inputs.forEach((input) => {
            let name = input.getAttribute('name')
            console.log(name)
            if(!name || !name.includes('logic')){
                return
            }
            const regex = /logic\[\d+\]/
            const replace = name.match(regex)[0];
            const value = `logic[${index}]`
            newName = name.replace(replace, value)
            input.setAttribute('name', newName)
        })
    }
}