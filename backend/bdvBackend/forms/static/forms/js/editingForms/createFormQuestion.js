import createButtons from "./createButtons.js";
import { addLogic, updateRules } from "./addLogic.js";
import { reIndex } from "./shiftQuestions.js";
import createSelect from "../../../../../static/js/customSelector/create-select.js";
import { addSearch } from "../../../../../static/js/select-search.js";

export default async function createFormQuestion(existing = null, atQuestion = null){
    const questionsDiv = document.querySelector('.questions');
    const questions = questionsDiv.querySelectorAll('.question');
    const index = questions.length;

    const question = document.createElement('div');
    question.setAttribute('class', 'question')
    question.setAttribute('index', index);
    if(atQuestion){
        let atIndex = parseInt(atQuestion.getAttribute('index'))
        questionsDiv.insertBefore(question, atQuestion);
        atQuestion.after(question);
    }
    else{
        questionsDiv.appendChild(question);
    }
    
    const response = await fetch('/forms/data/query/questions');
    const questionsList = await response.json();
    const qSelector = createSelect(questionsList.ids, questionsList.labels, true, 'question-type', questionsList.types, true);
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
    addSearch()
}

