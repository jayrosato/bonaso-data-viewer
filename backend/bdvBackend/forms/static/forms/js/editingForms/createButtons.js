import createFormQuestion from "./createFormQuestion.js";
import { addLogic } from "./addLogic.js";
import { moveQDown, moveQUp, removeQuestion } from "./shiftQuestions.js";

function createButton(text, className, onclick){
    const button = document.createElement('button');
    button.type = ('button');
    button.setAttribute('class', className)
    button.innerText = text;
    button.onclick = onclick;
    return button;
}

export default function createButtons(question){
    const buttons = document.createElement('div')
    buttons.setAttribute('class', 'buttons')
    question.appendChild(buttons)

    let index = parseInt(question.getAttribute('index'))
    const addQuestionButton = createButton('Add Question Below', 'addQuestionButton', () => createFormQuestion(null, question));
    buttons.appendChild(addQuestionButton)

    const addLogicButton = createButton('Add Logic', 'logicButton', () => addLogic(question));
    buttons.appendChild(addLogicButton)
    if(index == 0){
        addLogicButton.style.display = 'none';
    }
    const moveUpButton = createButton('Move Question Up', 'moveUpButton', () =>  moveQUp(question))
    buttons.appendChild(moveUpButton)
    const moveDownButton = createButton('Move Question Down', 'moveDownButton', () => moveQDown(question))
    buttons.appendChild(moveDownButton)
    const removeQuestionButton = createButton('Remove Question', 'removeButton', () => removeQuestion(question))
    buttons.appendChild(removeQuestionButton)
}