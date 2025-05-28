import createSearchSelector from "../../../../static/js/customSelector/create-search-selector.js";
import createSelect from "../../../../static/js/customSelector/create-select.js";
import createCheckbox from "../../../../static/js/createCheckbox.js";
let showLegend = true;
let showTargets = false;
let filters = [];

document.addEventListener('DOMContentLoaded', async function () {
    let location = document.querySelector('.questionSelect')
    const response = await fetch(`/forms/data/query/questions/responses`);
    const data = await response.json()

    //build a custom selector for selecting a specific question/indicator to view
    let qIDs = [];
    data.questions.forEach(item => {if(!qIDs.includes(item.question_id)){qIDs.push(item.question_id)}})
    let qText = [];
    data.questions.forEach(item => {if(!qText.includes(item.question_text)){qText.push(item.question_text)}})
    const questionSelector = createSearchSelector(qIDs, qText, true, () => selectDetails())
    location.appendChild(questionSelector)

    //build a custom axis selector for determining what goes on the x axis (y axis is always counts)
    const axisCont = document.querySelector('.axisCont')
    axisCont.style.display = 'none';
    location = document.querySelector('.axisSelect');
    const axisSelector = createSelect(['date', 'sex'], ['By Date', 'By Sex'], true)
    axisSelector.setAttribute('class', 'axisSelector')  
    axisSelector.onchange =() => getDataset(data)
    location.appendChild(axisSelector)
    
    //build a toggle for whether to show a legend or straight counts
    const legendCont = document.querySelector('.legendCont')
    legendCont.style.display == 'none';
    location = document.querySelector('.legendToggle');
    const legendToggle = createCheckbox('true', 'Show legend?')
    const legendCheck = legendToggle.querySelector('input')
    legendCheck.checked = true;
    location.appendChild(legendToggle)
    legendCheck.onchange = () => {
        showLegend = legendCheck.checked ? true : false;
        getDataset(data)
    }

    //build a toggle for displaying targets
    const targetCont = document.querySelector('.targetCont')
    targetCont.style.display == 'none';
    location = document.querySelector('.targetToggle');
    const targetToggle = createCheckbox('true', 'View Targets?')
    const targetCheck = targetToggle.querySelector('input')
    location.appendChild(targetToggle)
    targetCheck.onchange = () => {
        showTargets = targetCheck.checked ? true : false
    }

    //build filters
    const filtersDiv = document.querySelector('.filtersDiv');
    //filtersDiv.style.display = 'none';
    const filters = data.filters;
    data.filters.forEach(item => {
        const filter = document.createElement('div');
        filter.setAttribute('class', 'chartFilter');
        filter.setAttribute('id', item.name)
        const title = document.createElement('p');
        title.setAttribute('class', 'name')
        title.innerText = item.name;
        filter.appendChild(title);
        if(item.type == 'date' || item.type == 'number'){
            const low = document.createElement('input')
            const high = document.createElement('input')
            low.setAttribute('class', 'lowBound')
            high.setAttribute('class', 'highBound')
            low.onkeyup = () => updateFilters(filter, data)
            high.onkeyup = () => updateFilters(filter, data)
            low.type = item.type == 'number' ? 'number' : 'date';
            high.type = item.type == 'number' ? 'number' : 'date';
            if(item.type == 'date'){
                low.onchange= () => updateFilters(filter, data)
                high.onchange = () => updateFilters(filter, data)
            }
            filter.appendChild(low)
            filter.appendChild(high)
        }
        if(item.type == 'multiple'){
            const values = item.values
            values.forEach((value, index) => {
                const optionDiv = document.createElement('div');
                optionDiv.setAttribute('class', 'option');
                optionDiv.style.display = 'flex';
                optionDiv.style.flexDirection = 'row';
                const check = document.createElement('input');
                check.type = 'checkbox';
                check.value = value;
                check.onchange = () => updateFilters(filter, data)
                const label = document.createElement('p');
                label.innerText = item.labels !== undefined ? item.labels[index] : value;
                optionDiv.appendChild(check);
                optionDiv.appendChild(label);
                filter.appendChild(optionDiv)
            })
        }
        filtersDiv.appendChild(filter);
    })
});

function selectDetails(){
    const axisCont = document.querySelector('.axisCont')
    axisCont.style.display = '';
    const legendCont = document.querySelector('.legendCont')
    axisCont.style.display = '';
    const targetCont = document.querySelector('.targetCont')
    axisCont.style.display = '';
}


async function buildChart(labels, datasets, axis){
    const oldCanvas = document.getElementById(`chart`)
    if(oldCanvas){
        oldCanvas.remove()
        const canvas = document.createElement('canvas');
        canvas.setAttribute('id', `chart`);
        document.querySelector('.dashboard').appendChild(canvas)
    }
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data:{
            labels: labels,
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
                    title: {display: true, text: axis}
                },
                y: {
                    beginAtZero: true,
                    title: { display:true, text: 'Number of Responses'}
                }
            }
        }
    })
}

//group by raw response counts (total reached)
//factor in targets
function getDataset(data){
    const questionID = document.querySelector('.selector').getAttribute('value');
    if(questionID == ''){return};
    const axis = document.querySelector('.axisSelector').value;
    if(axis == ''){return};
    const question = data.questions.filter((question) => question.question_id == questionID)[0]
    const answers = question.answers
    let labels = [];
    let datasets = {};
    const groups = {}
    let respondents = []
    answers.forEach(item => {
        let axisGroup = null
        if(axis == 'date'){
            const rawDate = new Date(item.date)
            axisGroup = rawDate.toLocaleString('default',{month: 'short', year: 'numeric'});
        }
        else{axisGroup = item[axis]}
        
        const answer = item.answer_value || 'Unknown';
        if(!groups[axisGroup]) groups[axisGroup] = {};
        let pass = true
        console.log(filters)
        if(filters.length > 0){
            filters.forEach(filter => {
                if(item[filter.name] == undefined){
                    console.warn('Check the API. A filter value was not found in the answers object.')
                    return
                }
                if(filter.type=='multiple'){
                    if(!filter.values.includes(item[filter.name].toString())){
                        pass = false
                        return;
                    }
                }
                else if(filter.type=='date' || filter.type=='number'){
                    let low = filter.values.low;
                    let high = filter.values.high;
                    let value = item[filter.name]
                    if(filter.type == 'date'){
                        low = new Date(low);
                        low.setHours(0,0,0,0)
                        low = low.getTime()

                        high = new Date(high);
                        high.setHours(0,0,0,0)
                        high = high.getTime()

                        try{
                            value = new Date(value);
                            value.setHours(0,0,0,0)
                            value = value.getTime()
                        }
                        catch(err){
                            console.warn('Cannot apply date filter to field that contains invalid dates.')
                            return;
                        }
                    }
                    if(filter.type == 'number'){
                        try{
                            value = parseInt(value)
                        }
                        catch(err){
                            console.warn('Cannot apply numeric filter to field that does not contain numbers.')
                            return;
                        }
                    }
                    if(value < low || value > high){
                        pass = false
                        return;
                    }
                }
            })
        }
        if(!pass){
            return;
        }
        if(showLegend){
            groups[axisGroup][answer] = (groups[axisGroup][answer] || 0)+1;
        }
        else{
            if(answer.toLowerCase() == 'none' || answer.toLowerCase() == 'no'){
                return;
            }
            if(respondents.includes(item.respondent_id)){
                return;
            }
            else{
                respondents.push(item.respondent_id);
            }
            console.log(respondents)
            groups[axisGroup]['count'] = (groups[axisGroup]['count'] || 0)+1;
        }
    });
    console.log(groups)

    const axisGroups = Object.keys(groups);
    const allAnswers = [... new Set(answers.map(item => item.answer_value || 'Unknown'))];
    labels = axisGroups;
    if(showLegend){
        datasets = allAnswers.map(answer => {
            return {
                label: answer,
                data: axisGroups.map(group => groups[group][answer] || 0),
                backgroundColor: getRandomColor()
            };
        });
    }
    else{
        datasets = [{
            label: 'Total Number', 
            data: axisGroups.map(group => groups[group]['count'] || 0),
            backgroundColor: getRandomColor()
        }]
    }
    

    buildChart(labels, datasets, axis)
}

function updateFilters(filter, data){
    const inputs = filter.querySelectorAll('input')
    const name = filter.querySelector('.name').innerText
    let values = null
    let type = '';
    filters = filters.filter((filter) => filter.name != name)
    if(inputs[0].type == 'checkbox'){
        type = 'multiple'
        values = []
        inputs.forEach(input => {
            if(input.checked == true) values.push(input.value);
        })
        if(values.length == 0){
            getDataset(data)
            return;
        }
    }
    else{
        type = filter.querySelector('.lowBound').type == 'number' ? 'number':'date'
        let low = filter.querySelector('.lowBound').value;
        let high = filter.querySelector('.highBound').value;
        values = {'low':low, 'high':high}
        if(values.low == '' && values.high == ''){
            getDataset(data)
            return;
        }
    }
    filters.push({'name':name, 'values':values, 'type':type})
    getDataset(data)
}


function getRandomColor() {
    const r = Math.floor(Math.random() * 200);
    const g = Math.floor(Math.random() * 200);
    const b = Math.floor(Math.random() * 200);
    return `rgba(${r}, ${g}, ${b}, 0.6)`;
}
//const months = Object.keys(groups).sort((a,b) => new Date(a) - new Date(b));