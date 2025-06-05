import { updateRules } from "./addLogic.js";

export function moveQUp(question){
    let index = question.getAttribute('index');
    index = parseInt(index);
    const questionsList = document.querySelector('.questions');
    if(index==0){
        console.log('max uppage');
        return;
    }
    if(index == 1 && question.querySelector('.logicDiv') != null){
        const msg = document.getElementById('messages')
        msg.innerText = 'The first question of a form cannot contain logic. Please remove logic from this question before moving it up.'
        return;
    }
    const target = document.querySelector(`[index="${index-1}"]`);
    questionsList.insertBefore(question, target);
    reIndex()
}

export function moveQDown(question){
    let index = question.getAttribute('index');
    index = parseInt(index);
    const questionsList = document.querySelector('.questions');
    if(index == questionsList.children.length-1){
        console.log('max downage');
        return;
    }
    if(index==0){
        const nextQuestion = document.querySelector('[index="1"]')
        const checkLogic = nextQuestion.querySelector('.logicDiv')
        if(checkLogic){
            const msg = document.getElementById('messages')
            msg.innerText = 'The first question of a form cannot contain logic. Please remove logic from this question before moving it up.'
            return;
        }
    }
    const target = document.querySelector(`[index="${index+1}"]`);
    questionsList.insertBefore(target, question);
    reIndex()
}

export function removeQuestion(question){
    const questions = document.querySelector('.questions')
     if(questions.length == 1){
        const msg = document.getElementById('messages')
        msg.innerText = 'A form must have at least one question.'
        return;
    };
    questions.removeChild(question)
    reIndex()
}

export function reIndex(){
    const questions = document.querySelectorAll('.question')
    const numberQuestions = questions.length
    questions.forEach((question, index) => {
        if(index == 0){
            question.querySelector('.logicButton').style.display = 'none';
            question.querySelector('.moveUpButton').style.display = 'none';
        }
        else{
            question.querySelector('.logicButton').style.display = '';
            question.querySelector('.moveUpButton').style.display = '';
        }
        if(index == numberQuestions){
            question.querySelector('.moveDownButton').style.display = 'none';
        }
        else{
            question.querySelector('.moveDownButton').style.display = '';
        }
        question.setAttribute('index', index)
    })
    updateRules()
}