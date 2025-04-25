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

const div = document.querySelector('.questions');

const addQuestionButton = document.getElementById('add_question');
addQuestionButton.onclick = () => addQuestion();
const questions = document.getElementsByClassName('existing_question')
Array.from(questions).forEach((q) => {
    const removeOptionButton = document.createElement('button');
    removeOptionButton.innerText = 'Remove Question';
    removeOptionButton.onclick = () => {div.removeChild(q); index--};
    q.appendChild(removeOptionButton);
})
let index = questions.length
questions[0].querySelector('#id_index').value = 1


function addQuestion(){
    const questionDiv = document.getElementsByClassName('existing_question')[0].cloneNode(true);
    const indexInput = questionDiv.querySelector('#id_index')
    
    div.appendChild(questionDiv);

    const removeOptionButton = document.createElement('button');
    removeOptionButton.innerText = 'Remove Question';
    removeOptionButton.onclick = () => {div.removeChild(questionDiv); index--};
    questionDiv.appendChild(removeOptionButton);

    index ++
    indexInput.value = index
    
}