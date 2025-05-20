import createButtons from "./createButtons.js";
import { selectCreatorURL } from "./selectCreator.js";
import { addLogic, updateRules } from "./addLogic.js";
import { reIndex } from "./shiftQuestions.js";
export default async function createFormQuestion(existing = null, atQuestion = null){
    const questionsDiv = document.querySelector('.questions');
    const questions = questionsDiv.querySelectorAll('.question');
    const index = questions.length;

    const question = document.createElement('div');
    question.setAttribute('class', 'question')
    question.setAttribute('index', index);
    if(atQuestion){
        let atIndex = parseInt(atQuestion.getAttribute('index'))
        console.log(atIndex)
        questionsDiv.insertBefore(question, atQuestion);
        atQuestion.after(question);
    }
    else{
        questionsDiv.appendChild(question);
    }
    

    const qSelector = await selectCreatorURL('question', '/forms/data/query/questions');
    qSelector.setAttribute('name', 'question');
    qSelector.setAttribute('class', 'questionSelector');
    qSelector.onchange = () => updateRules()
    question.appendChild(qSelector);
    createButtons(question);

    if(existing){
        console.log(existing)
        question.setAttribute('fqID', existing.id)
        qSelector.value = existing.question_id
        qSelector.setAttribute('question-type', existing.question_type)
        if(existing.logic){
            addLogic(question, existing)
        }
    }
    reIndex()
}

