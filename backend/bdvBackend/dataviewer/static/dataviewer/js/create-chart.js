import createSearchSelector from "../../../../static/js/customSelector/create-search-selector.js";
import createSelect from "../../../../static/js/customSelector/create-select.js";


document.addEventListener('DOMContentLoaded', async function () {
    let target = document.querySelector('.questionSelect')
    const response = await fetch('/forms/data/query/questions')
    const data = await response.json()
    const questionSelector = createSearchSelector(data.ids, data.labels, true, () => showStep2(questionSelector))
    target.appendChild(questionSelector)

    const step2 = document.querySelector('.step2')
    step2.style.display = 'none';

    target = document.querySelector('.axisSelect');
    const axisSelector = createSelect(['date'], ['By Date'], true)
    axisSelector.onchange =() => showStep3(questionSelector, axisSelector)
    target.appendChild(axisSelector)
});

function showStep2(question){
    const step2 = document.querySelector('.step2')
    step2.style.display = '';
}

async function showStep3(questionSelect, axisSelect){
    console.log(questionSelect)
    const question = questionSelect.querySelector('.selector').getAttribute('value')
    const axis = axisSelect.value
    const response = await fetch(`/forms/data/query/questions/${question}/responses`);
    const data = await response.json()
    if(axis == 'date'){
        const groups = {};
        data.forEach(item => {
            const rawDate = new Date(item.date)
            const month = rawDate.toLocaleString('default',{month: 'short', year: 'numeric'});
            const answer = item.answer_value || 'Unknown';
            if (!groups[month]) groups[month] = {};
            groups[month][answer] = (groups[month][answer] || 0) + 1;
        });

        const months = Object.keys(groups).sort((a,b) => new Date(a) - new Date(b));
        const allAnswers  = [... new Set(data.map(item => item.answer_value || 'Unknown'))];
        const datasets = allAnswers.map(answer =>{
            return {
                label: answer,
                data: months.map(month => groups[month][answer] || 0),
                backgroundColor: getRandomColor()
            };
        });
        const ctx = document.getElementById('chart').getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data:{
                labels: months,
                datasets: datasets
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {position: 'bottom'}
                },
                scales: {
                    x: {
                        stacked: false,
                        title: {display: true, text: 'Month'}
                    },
                    y: {
                        beginAtZero: true,
                        title: { display:true, text: 'Number of Responses'}
                    }
                }
            }
        })

    }
}
function getRandomColor() {
    const r = Math.floor(Math.random() * 200);
    const g = Math.floor(Math.random() * 200);
    const b = Math.floor(Math.random() * 200);
    return `rgba(${r}, ${g}, ${b}, 0.6)`;
}