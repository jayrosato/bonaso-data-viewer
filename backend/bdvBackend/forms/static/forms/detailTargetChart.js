const targetPasser = document.getElementById('target')
const targetID = targetPasser.getAttribute('target')

window.onload = () => createTargetChart()

async function createTargetChart() {
    try{
        Chart.defaults.color = "#ffffff";
        const response = await fetch(`/forms/data/query/targets/${targetID}`)
        const data = await response.json()
        const canvas = document.getElementById(`targetChart`)
        targetChart = new Chart(canvas,{
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false
            }})
    }
    catch(err){
        console.error(err)
    }

}
