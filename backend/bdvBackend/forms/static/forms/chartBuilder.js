const ctx = document.getElementById('chart').getContext('2d');
const targetPasser = document.getElementById('target')
const targetId = targetPasser.getAttribute('target')
try{
    Chart.defaults.color = "#ffffff";
    fetch(`/forms/data/query/target/${targetId}`)
        .then(response => response.json())
        .then(data => {
            new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    });
}
catch(err){
    console.error(err)
}

const updateQuestionButton = document.getElementById('qSelect')
updateQuestionButton.onclick = () => updateQuestionChart()
let questionChart;

function updateQuestionChart(){
    if(questionChart instanceof Chart){
        questionChart.destroy()
    }
        const Qctx = document.getElementById('Qchart').getContext('2d');
        let question = document.getElementById('id_question').value;
        if(!question){
            question = 1    
        }
        try{
            Chart.defaults.color = "#ffffff";
            fetch(`/forms/data/getq/${question}`)
                .then(response => response.json())
                .then(data => {
                    questionChart = new Chart(Qctx, {
                    type: 'bar',
                    data: data,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            });
        }
        catch(err){
            console.error(err)
        }
    }