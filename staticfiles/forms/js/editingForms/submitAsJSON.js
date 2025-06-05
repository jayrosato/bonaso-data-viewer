import { addWarning, clearWarning, initWarning } from "../../../../../static/js/customWarning.js";

export default async function submitAsJson(csrftoken, formID=null){
    clearWarning();
    let flag = false;
    const formName = document.getElementById('id_form_name').value
    if(formName == ''){
        flag=true;
        addWarning('Please enter a name for this form!');
    }
    const organization = document.getElementById('id_organization').value
    if(organization == ''){
        flag=true;
        addWarning('Please select an organizaiton.');
    }
    const startDate = document.getElementById('id_start_date').value
    if(startDate == ''){
        flag=true;
        addWarning('Please enter a start date.');
    }
    const endDate = document.getElementById('id_end_date').value
    if(endDate == ''){
        flag=true;
        addWarning('Please select an organizaiton.');
    }
    const form = {
        'form_name': formName,
        'organization': organization,
        'start_date': startDate,
        'end_date': endDate,
        'form_questions': []
    };

    const questions = document.querySelectorAll('.question');
    let questionSequence = []
    questions.forEach((question, index) => {
        const checkQuestion = question.querySelector('.questionSelector');
        if(!checkQuestion || checkQuestion.value == ''){
            flag = true;
            addWarning(`Please select a valid question at index ${index+1}.`);
            return;
        }
        const fqID = question.hasAttribute('fqID') ? question.getAttribute('fqID') : null
        const formQuestion = {
            'id': fqID,
            'on_match': 'Show',
            'question': question.querySelector('.questionSelector').value,
            'index': index,
            'logic': {}
        };
        const checkLogic = question.querySelector('.logicDiv');
        if(checkLogic){
            const checkRules = checkLogic.querySelectorAll('.ruleDiv');
            if(!checkRules){
                flag = true
                addWarning(`Question at index ${index+1} has logic, but no rules. Please remove logic for this question or add a rule.`);
            }
            let logic = formQuestion.logic
            logic.conditional_operator = checkLogic.querySelector('.operatorSelector') ? checkLogic.querySelector('.operatorSelector').value: 'AND';
            logic.rules = [];
            checkRules.forEach((rule) => {
                const parentQuestion = rule.querySelector('.parentQuestionSelector').value;
                if(parentQuestion == ''){
                    flag = true;
                    addWarning(`Please select a valid question for all rules at question ${index+1}.`);
                    return;
                }
                if(!questionSequence.includes(parentQuestion) || parentQuestion == fqID){
                    addWarning(`For logic to work properly, the parent question for logic at ${index+1} must be a question that appears before this one in the form and must be a different question.`);
                    flag = true;
                    return;
                }
                const expectedValue = rule.querySelector('.valueInput').value;
                if(expectedValue == ''){
                    flag = true;
                    addWarning(`Please select/enter valid values for all rules at question ${index+1}.`);
                    return;
                }
                const limitOptions = rule.querySelector('.limitOptions') && rule.querySelector('.limitOptions').checked == true ? true : false;
                let negateValue = rule.querySelector('.negateSelector') ? rule.querySelector('.negateSelector').value : 'false';
                negateValue = negateValue=='true' ? true : false;
                const valueComparison = rule.querySelector('.comparisonSelector') ? rule.querySelector('.comparisonSelector').value : null;
                
                const logicRule ={
                    'parent_question': parentQuestion,
                    'expected_value': expectedValue,
                    'limit_options': limitOptions,
                    'value_comparison': valueComparison,
                    'negate_value': negateValue,
                }
                logic.rules.push(logicRule);
            })
        }
        questionSequence.push(question.querySelector('.questionSelector').value);
        form.form_questions.push(formQuestion);
    })
    if(flag){
        initWarning();
        return;
    }

    const url = formID ? `/forms/${formID}/update` : '/forms/create'
    const response = await fetch(url, {
        method: 'POST', 
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify(form),
    });
    const result = await response.json()
    if(result.redirect){
        window.location.href = result.redirect;
    }
    else if(result.warning){
        addWarning(result.warning);
    }
}   