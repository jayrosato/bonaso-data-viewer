import createButtons from "./createButtons.js";
import { selectCreatorURL } from "./selectCreator.js";

export default async function createFormQuestion(existing = null, index=null){
    const questionsDiv = document.querySelector('.questions');
    const questions = questionsDiv.querySelectorAll('.question');
    const index = questions.length - 1;

    const question = document.createElement('div');
    question.setAttribute('index', index);
    questionsDiv.appendChild(question);

    const qSelector = await selectCreatorURL('question', '/forms/data/query/questions');
    console.log(qSelector)
    qSelector.setAttribute('name', 'question');
    qSelector.setAttribute('class', 'questionSelector');
    question.appendChild(qSelector);
    createButtons(question);

    if(existing){
        qSelector.value = existing.question_id
        qSelector.setAttribute('question-type', existing.question_type)
        if(existing.logic){
            addLogic(existing.logic)
        }
    }
}

