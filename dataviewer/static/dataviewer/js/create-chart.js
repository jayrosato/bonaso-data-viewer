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
    const targetResponse = await fetch('/organizations/targets/query')
    const targets = await targetResponse.json()
    data.targets = targets;
    //build a custom selector for selecting a specific question/indicator to view
    let qIDs = [];
    data.questions.forEach(item => {if(!qIDs.includes(item.question_id)){qIDs.push(item.question_id)}})
    let qText = [];
    data.questions.forEach(item => {if(!qText.includes(item.question_text)){qText.push(item.question_text)}})
    const questionSelector = createSearchSelector(qIDs, qText, true, () => selectDetails(data, targets), 'Select a question...')
    location.appendChild(questionSelector)

    //build a custom axis selector for determining what goes on the x axis (y axis is always counts)
    const axisCont = document.querySelector('.axisSelect')
    axisCont.style.display = 'none';
    location = document.querySelector('.axisSelect');
    const axisSelector = createSelect(['count','date', 'sex', 'district', 'organization'], ['Raw Count','By Date', 'By Sex', 'By District', 'By Organization'], true)
    axisSelector.setAttribute('class', 'axisSelector')  
    axisSelector.onchange =() => getDataset(data)
    location.appendChild(axisSelector)
    
    //build a toggle for whether to show a legend or straight counts
    const legendCont = document.querySelector('.legendToggle')
    legendCont.style.display = 'none';
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
    const targetCont = document.querySelector('.targetToggle')
    targetCont.style.display = 'none';
    location = document.querySelector('.targetToggle');
    const targetToggle = createCheckbox('true', 'View Targets?')
    const targetCheck = targetToggle.querySelector('input')
    location.appendChild(targetToggle)
    targetCheck.onchange = () => {
        showTargets = targetCheck.checked ? true : false
        getDataset(data)
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
        title.innerText = item.name.charAt(0).toUpperCase() + item.name.slice(1);
        filter.appendChild(title);
        if(item.type == 'date' || item.type == 'number'){
            const label1 = document.createElement('label')
            label1.innerText = 'Between'
            const low = document.createElement('input')
            const label2 = document.createElement('label')
            label2.innerText = 'And'
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
            filter.appendChild(label1)
            filter.appendChild(low)
            filter.appendChild(label2)
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

function selectDetails(data, targets){
    const qID = document.querySelector('.selector').getAttribute('value');
    const axisCont = document.querySelector('.axisSelect')
    axisCont.style.display = '';
    const legendCont = document.querySelector('.legendToggle')
    legendCont.style.display = '';

    const targetCont = document.querySelector('.targetToggle')
    const showTargets = targets.some(target => target.question == qID)
    if(showTargets){
        targetCont.style.display = '';
    }
    else{
        targetCont.style.display = 'none';
    }
    if(axisCont.value != ''){
        getDataset(data)
    }
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


function getDataset(data){
    const questionID = document.querySelector('.selector').getAttribute('value');
    if(questionID == ''){return};
    const axis = document.querySelector('.axisSelector').value;
    if(axis == ''){return};
    const question = data.questions.filter((question) => question.question_id == questionID)[0]
    const answers = question.answers
    let targets = null;
    if(showTargets){
        targets = data.targets.filter((target) => target.question == questionID);
    }
    let labels = [];
    let datasets = {};
    const groups = {};
    let respondents = [];
    let axisValueLabels = [];
    console.log(data)
    answers.forEach(item => {
        let axisGroup = null

        if(axis == 'count'){
            axisGroup = 'Count';
        }
        else if(axis == 'date'){
            const rawDate = new Date(item.date)
            axisGroup = rawDate.toLocaleString('default',{month: 'short', year: 'numeric'});
        }
        else{
            axisGroup = item[axis]
        }
        if(axis == 'organization'){
            axisValueLabels.push({'id': item.organization, 'name': item.organization_name})
        }
        
        const answer = item.answer_value || 'Unknown';
        if(!groups[axisGroup]) groups[axisGroup] = {};
        if(filters.length > 0){
            let pass = testFilter(item);
            if(!pass){
                return;
            }
        }
        let amount = 1;
        if(question.question_type == 'Number'){
            if(isNaN(item.answer_value)){
                console.warn(`${question} was expecting a number.`)
                return;
            }
            amount = parseInt(item.answer_value);
        }
        if(question.question_type == 'Number'){
            groups[axisGroup]['sum'] = (groups[axisGroup]['count'] || 0) + amount;
        }
        else if(showLegend){
            groups[axisGroup][answer] = (groups[axisGroup][answer] || 0)+ amount;
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
            groups[axisGroup]['count'] = (groups[axisGroup]['count'] || 0) + amount;
        }
    });
    const targetGroups = {};
    if(targets){
        console.log(targets)
        let targetGroup = null;
        targets.forEach((target) => {
            if(axis=='date'){
                const rawDate = new Date(target.end)
                targetGroup = rawDate.toLocaleString('default', {month: 'short', year: 'numeric'})
                target.date = target.end
            }
            else{
                try{
                    targetGroup = target[axis];
                }
                catch(err){
                    targetGroup = null;
                    console.warn('This axis type is not applicable for targets.')
                }
            }
            if(filters.length > 0){
                let pass = testFilter(target);
                if(!pass){
                    return;
                }
            }
            const amount = target.amount || 0;
            if(targetGroup){
                if(!targetGroups[targetGroup]) targetGroups[targetGroup] = 0;
                targetGroups[targetGroup] += amount;
            }
            else{
                if(!targetGroups['target']) targetGroups['target'] = 0;
                targetGroups['target'] += amount;
            }
        })
    }

    let axisGroups = Object.keys(groups);
    let targetAxisGroups = Object.keys(targetGroups)
    if(axis=='date'){
        axisGroups = Object.keys(groups).sort((a,b) => new Date(a) - new Date(b));
        targetAxisGroups = Object.keys(groups).sort((a,b) => new Date(a) - new Date(b));
    }

    const allAnswers = [... new Set(answers.map(item => item.answer_value || 'Unknown'))];
    labels = axisGroups;
    if(axisValueLabels.length > 0){
        let tempGroups = []
        axisGroups.forEach(group => {
            const pair = axisValueLabels.find(item => item.id == group);
            tempGroups.push(pair.name)
        })
        labels = tempGroups
    }
    if (targets && targetAxisGroups === 'target') {
        labels.push('Target');
    }

    if(question.question_type == 'Number'){
        datasets = [{
            label: 'Sum of Total Acheived', 
            data: axisGroups.map(group => groups[group]['sum'] || 0),
            backgroundColor: getRandomColor()
        }]
    }
    else if(showLegend){
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
            label: 'Acheived Count', 
            data: axisGroups.map(group => groups[group]['count'] || 0),
            backgroundColor: getRandomColor()
        }]
    }
    if(targets){
        let data = null
        if(targetAxisGroups == 'target' && axis != 'count'){
            labels.push('Target')
            const targetValue = targetGroups['target'] || 0;
            data = labels.map((label, index) => index === labels.length - 1 ? targetValue : null)
        }
        else{
            data = targetAxisGroups.map(group => targetGroups[group] || 0)
        }
        datasets.push({
            label: 'Target',
            data: data,
            backgroundColor: '#FF0000'
        })
    }
    buildChart(labels, datasets, axis)
}

function updateFilters(filter, data){
    const inputs = filter.querySelectorAll('input')
    const name = filter.querySelector('.name').innerText.toLowerCase()
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

function testFilter(item){
    let pass = filters.every((filter) => {
        if(item[filter.name] == undefined){
        console.warn('Check the API. A filter value was not found in the answers object.')
        return true;
        }
        if(filter.type=='multiple'){
            if(!filter.values.includes(item[filter.name].toString())){
                return false;
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
                    return true;
                }
            }
            if(filter.type == 'number'){
                try{
                    value = parseInt(value)
                }
                catch(err){
                    console.warn('Cannot apply numeric filter to field that does not contain numbers.')
                    return true;
                }
            }
            if(value < low || value > high){
                return false;
            }
        }
        return true
    })
    return pass
}

function getRandomColor() {
    const r = Math.floor(Math.random() * 200);
    const g = Math.floor(Math.random() * 200);
    const b = Math.floor(Math.random() * 200);
    return `rgba(${r}, ${g}, ${b}, 0.6)`;
}
//const months = Object.keys(groups).sort((a,b) => new Date(a) - new Date(b));