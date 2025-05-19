export async function selectCreatorURL(type, url, existingID = null){
    const selector = document.createElement('select');
    const nullOption = document.createElement('option')
    nullOption.text = '-----'
    selector.appendChild(nullOption)
    if(type=='question'){
        try{
            const response = await fetch(url);
            const questions = await response.json();
            questions.ids.forEach((question, index) => {
                const id = questions.ids[index]
                const label = questions.labels[index]
                const type = questions.types[index]
                const option = document.createElement('option')
                option.setAttribute('value', id)
                option.innerText = label
                option.setAttribute('question-type', type)
                selector.appendChild(option)
            });
            if(existingID){
                selector.value = existingID
            }
            return selector
        }
        catch(err){
            console.log('Failed to fetch questions: ', err)
        }
    }
}