import createSelect from "../../../../../static/js/customSelector/create-select.js";

export function addLogic(question, existing = null){
    const logicDiv = document.createElement('div');
    logicDiv.setAttribute('class', 'logicDiv')
    question.appendChild(logicDiv);
    const logicLabel = document.createElement('p');
    logicLabel.innerText = `Question Logic:`;
    logicDiv.appendChild(logicLabel);

    const operator = createSelect(['AND', 'OR'])
    operator.setAttribute('class', 'operatorSelector')
    logicDiv.appendChild(operator)
    operator.style.display = 'none' //hide operators by default, since it doesn't make sense if there is only one rule
    if(existing){
        const checkRules = existing.logic.rules;
        if(!checkRules || checkRules.length == 0){
            console.warn(`Logic for question ${existing.question} has no rules. Please remove logic or add rules.`);
            return;
        }
        if(checkRules.length > 1){
            operator.style.display = '';
        }
        checkRules.forEach(rule => {
            addRule(question, rule)
        });
        console.log(existing.logic)
        operator.value = existing.logic.conditional_operator
    }
    else{
        addRule(question)
    }
    const addRuleButton = document.createElement('button')
    addRuleButton.type = ('button')
    addRuleButton.innerText = 'Add Another Rule'
    addRuleButton.onclick = () => addRule(question);
    logicDiv.appendChild(addRuleButton)

    const qlButton = question.querySelector('.logicButton')
    qlButton.onclick = () => {
        question.removeChild(logicDiv)
        qlButton.innerText = 'Add Question Logic'
        qlButton.onclick = () => addLogic(question)
    }
    qlButton.innerText = 'Remove Question Logic'
}

export function addRule(question, existing=null){
    const ruleDiv = document.createElement('div');
    ruleDiv.setAttribute('class', 'ruleDiv');
    const logicDiv = question.querySelector('.logicDiv');
    logicDiv.appendChild(ruleDiv);
    const ruleLabel = document.createElement('p')
    ruleDiv.appendChild(ruleLabel)

    const checkRules = logicDiv.querySelectorAll('.ruleDiv');
    const ruleIndex = checkRules.length
    ruleLabel.innerText = `Rule ${ruleIndex}:`

    if(ruleIndex > 1){
        const operator = logicDiv.querySelector('.operatorSelector');
        operator.style.display = ''; //show the operator if there is more than one rule
        //also display the remove button if there is more than one rule
        const removeRuleButton = document.createElement('button')
        removeRuleButton.type = ('button')
        removeRuleButton.innerText = 'Remove this Rule'
        removeRuleButton.onclick = () => {logicDiv.removeChild(ruleDiv)}
        ruleDiv.appendChild(removeRuleButton)
    }
    
    const conditionalIndex = parseInt(question.getAttribute('index'))
    const formQuestions = document.querySelectorAll('.questionSelector')
    let parentQuestionIDs = []
    let parentQuestionText = []
    let parentQuestionType = []
    formQuestions.forEach((formQuestion, index) =>{
        if(index >= conditionalIndex || formQuestion.value == ''){
            return;
        }
        const questionID = formQuestion.value
        const selectedOption = formQuestion.options[formQuestion.selectedIndex]
        parentQuestionIDs.push(questionID)
        parentQuestionText.push(selectedOption.text)
        parentQuestionType.push(selectedOption.getAttribute('question-type'))
    })
    const parentQuestionSelector = createSelect(parentQuestionIDs, parentQuestionText, true, 'question-type', parentQuestionType)
    parentQuestionSelector.setAttribute('class', 'parentQuestionSelector')
    parentQuestionSelector.onchange = () => updateRule(ruleDiv)
    ruleDiv.appendChild(parentQuestionSelector)

    if(existing){
        parentQuestionSelector.value = existing.parent_question_id;
        updateRule(ruleDiv, existing);
    }
}

//remove old stuff on change here
export async function updateRule(ruleDiv, existing=null){
    const existingValueInput = ruleDiv.querySelector('.valueInput')
    if(existingValueInput){
        ruleDiv.removeChild(existingValueInput)
    }
    const existingComparisonSelector = ruleDiv.querySelector('.comparisonSelector')
    if(existingComparisonSelector){
        ruleDiv.removeChild(existingComparisonSelector)
    }
    const existingLimitOptions = ruleDiv.querySelector('.limitOptionsDiv')
    if(existingLimitOptions){
        ruleDiv.removeChild(existingLimitOptions)
    }
    const existingNegateSelector = ruleDiv.querySelector('.negateSelector')
    if(existingNegateSelector){
        ruleDiv.removeChild(existingNegateSelector)
    }

    const parentQuestionSelector = ruleDiv.querySelector('.parentQuestionSelector')
    const parentQuestionValue = parentQuestionSelector.value
    if(parentQuestionValue == ''){
        return
    }

    const parentQuestion = parentQuestionSelector.selectedOptions[0]
    const parentQuestionType = parentQuestion.getAttribute('question-type')
    if(parentQuestionType == 'Multiple Selections' || parentQuestionType =='Single Selection'){
            const negateSelector = createSelect([false, true], ['WHEN VALUE IS', 'WHEN VALUE IS NOT']);
            negateSelector.setAttribute('class', 'negateSelector')
            ruleDiv.appendChild(negateSelector);
            negateSelector.value = existing && existing.negate_value ? true:false;

            const response = await fetch(`/forms/data/query/questions/${parentQuestionValue}/meta`);
            const options = await response.json();
            const valueInput = createSelect(options.option_ids, options.option_text, true);
            const anyOption = document.createElement('option');
            anyOption.value = 'any';
            anyOption.text = 'Anything Selected';
            valueInput.appendChild(anyOption);

            const noneOption = document.createElement('option');
            noneOption.value = 'none';
            noneOption.text = 'Nothing Selected';
            valueInput.appendChild(noneOption);
            ruleDiv.appendChild(valueInput);
            valueInput.value = existing ? existing.expected_values : '';
            valueInput.setAttribute('class', 'valueInput');
    }
    if(parentQuestionType == 'Yes/No'){
        const valueInput = createSelect(['Yes', 'No'])
        valueInput.setAttribute('class', 'valueInput');
        ruleDiv.appendChild(valueInput);
        valueInput.value = existing ? existing.expected_values : '';
    }
    
    if(parentQuestionType == 'Text'){
        const valueInput = document.createElement('input');
        valueInput.setAttribute('id', 'valueInput');
        valueInput.setAttribute('type', 'text');
        valueInput.setAttribute('class', 'valueInput');
        ruleDiv.appendChild(valueInput);
        const comparisonSelector = createSelect(['MATCHES', 'CONTAINS', 'DOES NOT CONTAIN']);
        comparisonSelector.setAttribute('class', 'comparisonSelector');
        ruleDiv.appendChild(comparisonSelector);
        valueInput.value = existing ? existing.expected_values : '';
        comparisonSelector.value = existing ? existing.value_comparison : '';
    }
    
    if(parentQuestionType == 'Number'){
        const valueInput = document.createElement('input');
        valueInput.setAttribute('id', 'valueInput');
        valueInput.setAttribute('type', 'number');
        valueInput.setAttribute('class', 'valueInput')
        ruleDiv.appendChild(valueInput);
        const comparisonSelectorNum = createSelect(['EQUAL TO', 'GREATER THAN', 'LESS THAN']);
        comparisonSelectorNum.setAttribute('class', 'comparisonSelector');
        ruleDiv.appendChild(comparisonSelectorNum);
        valueInput.value = existing ? existing.expected_values : '';
        comparisonSelectorNum.value = existing ? existing.value_comparison : '';
    }
    

    if(parentQuestionType == 'Multiple Selections'){
        const questionSelector = ruleDiv.parentElement.parentElement.querySelector('.questionSelector')
        const questionSelectorOption = questionSelector.options[questionSelector.selectedIndex]
        const type = questionSelectorOption.getAttribute('question-type')
        if(type == 'Multiple Selections'){
            const limitOptionsDiv = document.createElement('div');
            limitOptionsDiv.setAttribute('class', 'limitOptionsDiv');
            ruleDiv.appendChild(limitOptionsDiv);

            const limitOptionsLabel = document.createElement('label');
            limitOptionsLabel.innerText = 'Limit Options based on Question';
            const limitOptions = document.createElement('input');
            limitOptions.setAttribute('type', 'checkbox');
            limitOptions.setAttribute('class', 'limitOptions');
            limitOptionsDiv.appendChild(limitOptionsLabel);
            limitOptionsDiv.appendChild(limitOptions);
            limitOptions.value = existing && existing.limit_options ? limitOptions.checked = true : limitOptions.checked = false
        }
    }
}
export function updateRules(){
    const questions = document.querySelectorAll('.question');
    let questionIDs = []
    let questionText = []
    let questionTypes = []
    questions.forEach((question) => {
        const questionSelector = question.querySelector('.questionSelector')
        const questionIndex = parseInt(question.getAttribute('index'))
        const selectedOption = questionSelector.options[questionSelector.selectedIndex]
        questionIDs.push(questionSelector.value);
        questionText.push(selectedOption.text)
        questionTypes.push(selectedOption.getAttribute('question-type'))
    })

    const parentQuestionSelectors = document.querySelectorAll('.parentQuestionSelector');
    if(!parentQuestionSelectors){
        return;
    }
    parentQuestionSelectors.forEach(selector => {
        let qIndex = parseInt(selector.parentElement.parentElement.parentElement.getAttribute('index'))
        const oldOptions = selector.querySelectorAll('option')
        const oldOptionIDs = [];
        oldOptions.forEach(option => {
            oldOptionIDs.push(option.value);
            if(!questionIDs.includes(option.value) && option.value != ''){
                option.remove();
            }
        });
        questionIDs.forEach((id, index) => {
            if(!oldOptionIDs.includes(id) && id != ''){
                if(qIndex <= index){return;}
                const option = document.createElement('option');
                option.value = id;
                option.innerText = questionText[index];
                option.setAttribute('question-type', questionTypes[index]);
                selector.appendChild(option);
            }
        });
    });
}