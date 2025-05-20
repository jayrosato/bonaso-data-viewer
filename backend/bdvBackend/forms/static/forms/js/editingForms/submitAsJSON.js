

export default async function submitAsJson(csrftoken, formID=null){
    const msg = document.getElementById('messages');
    msg.innerText = '';
    let flag = false;
    const formName = document.getElementById('id_form_name').value
    if(formName == ''){
        flag=true;
        msg.innerText += '\nPlease enter a name for this form!';
    }
    const organization = document.getElementById('id_organization').value
    if(organization == ''){
        flag=true;
        msg.innerText += '\nPlease select an organizaiton.';
    }
    const startDate = document.getElementById('id_start_date').value
    if(startDate == ''){
        flag=true;
        msg.innerText += '\nPlease enter a start date.';
    }
    const endDate = document.getElementById('id_end_date').value
    if(endDate == ''){
        flag=true;
        msg.innerText += '\nPlease select an organizaiton.';
    }
    const form = {
        'form_name': formName,
        'organization': organization,
        'start_date': startDate,
        'end_date': endDate,
        'form_questions': []
    };

    const questions = document.querySelectorAll('.question');

    questions.forEach((question, index) => {
        const checkQuestion = question.querySelector('.questionSelector');
        console.log
        if(!checkQuestion || checkQuestion.value == ''){
            flag = true;
            msg.innerText += `\nPlease select a valid question at index ${index+1}.`;
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
                msg.innerText += `\nQuestion at index ${index+1} has logic, but no rules. Please remove logic for this question or add a rule.`;
            }
            let logic = formQuestion.logic
            logic.conditional_operator = checkLogic.querySelector('.operatorSelector') ? checkLogic.querySelector('.operatorSelector').value: 'AND';
            logic.rules = [];
            checkRules.forEach((rule) => {
                const parentQuestion = rule.querySelector('.parentQuestionSelector').value;
                if(parentQuestion == ''){
                    flag = true;
                    msg.innerText += `\nPlease select a valid question for all rules at question ${index+1}.`;
                    return;
                }
                const expectedValue = rule.querySelector('.valueInput').value;
                if(expectedValue == ''){
                    flag = true;
                    msg.innerText += `\nPlease select/enter valid values for all rules at question ${index+1}.`;
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
        form.form_questions.push(formQuestion);
    })
    console.log(form)
    if(flag){
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
        msg.innerText += result.warning;
    }
    console.log(result)    
}   