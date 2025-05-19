export default function createButtons(question){
    const buttons = document.createElement('div')
    buttons.setAttribute('class', 'buttons')
    question.appendChild(buttons)

    const addQuestionButton = document.createElement('button');
    addQuestionButton.innerText = 'Add Question Below';
    addQuestionButton.type = ('button');
    addQuestionButton.onclick = () => createFormQuestion(question);
    buttons.appendChild(addQuestionButton);

    const addQuestionLogicButton = document.createElement('button');
    addQuestionLogicButton.innerText = 'Add Question Logic'
    addQuestionLogicButton.setAttribute('class', 'addQlButton')
    addQuestionLogicButton.type = ('button');
    let index = question.getAttribute('index');
    index = parseInt(index);
    if(index == 0){
        addQuestionLogicButton.onclick = () => msg.innerText = 'The first questionuestion of a form must always be shown, and therefore cannot have logic.'
        addQuestionLogicButton.style.backgroundColor = 'grey'
    }
    else{
        addQuestionLogicButton.onclick = () => addQuestionLogic(question);
        buttons.appendChild(addQuestionLogicButton)
    }
    buttons.append(addQuestionLogicButton)

    const shiftQUpButton = document.createElement('button');
    shiftQUpButton.innerText = 'Move Question Up';
    shiftQUpButton.setAttribute('type', 'button');
    shiftQUpButton.onclick = () => shiftQUp(question);
    buttons.appendChild(shiftQUpButton);

    const shiftQDownButton = document.createElement('button');
    shiftQDownButton.innerText = 'Move Question Down';
    shiftQDownButton.setAttribute('type', 'button');
    shiftQDownButton.onclick = () => shiftQDown(question);
    buttons.appendChild(shiftQDownButton);

    const removeQuestionButton = document.createElement('button');
    removeQuestionButton.innerText = 'Remove Question';
    removeQuestionButton.type = ('button');
    removeQuestionButton.onclick = () => removeQuestion(question);
    buttons.appendChild(removeQuestionButton);
}