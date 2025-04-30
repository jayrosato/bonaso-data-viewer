const dashboard = document.getElementsByClassName('dashboard')[0];
const addChartButton = document.getElementById('addChartButton');
addChartButton.onclick=()=>createChart()
let index = 0

Chart.defaults.color = "#ffffff";
class DBChart{
    constructor(){
        this.id = index
        this.cont = document.createElement('div');
        this.cont.setAttribute('class', 'chartCont');
        dashboard.appendChild(this.cont)
        const canvas = document.createElement('canvas');
        canvas.setAttribute('id', `chart${this.id}`);
        this.cont.appendChild(canvas)
        index++
    }

    async createQSelect(){
        const response = await fetch('/forms/data/query/questions')
        const data = await response.json()
        const qSelect = document.createElement('select')
        qSelect.setAttribute('id', `selector${this.id}`)
        qSelect.onchange = () => this.updateChart(qSelect)
        for(let i=0; i<data.ids.length; i++){
            const option = document.createElement('option')
            option.value = data.ids[i]
            option.innerText = data.labels[i]
            qSelect.appendChild(option)
        }
        this.cont.appendChild(qSelect)
    }
    async createChart(url, type){
        const response = await fetch(url)
        const data = await response.json()
        this.newChart = new Chart(`chart${index-1}`,{
                type: type,
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }})
    }
    async updateChart(question){
        const qID = question.value
        const response = await fetch(`/forms/data/query/questions/${qID}`)
        const data = await response.json()

        const oldCanvas = document.getElementById(`chart${this.id}`)
        if(oldCanvas){
            oldCanvas.remove()
            const canvas = document.createElement('canvas');
            canvas.setAttribute('id', `chart${this.id}`);
            this.cont.appendChild(canvas)
        }
        this.newChart = new Chart(`chart${this.id}`,{
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }})
    }
};

function createChart(){
    const chart = new DBChart
    chart.createQSelect()
    chart.createChart('/forms/data/get', 'bar')
}