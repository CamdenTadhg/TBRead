let $postDaysButton = $('#post_days_button');
let $lastPostDate = $('#last_post_date');
let $postingFrequency = $('#posting_frequency');
let $postingDay = $('#posting_day')

//event listener for setting posting days
$postDaysButton.on('click', async function(event){
    event.preventDefault();
    console.log('post days button clicked')
    $modalBody.find('.error-div').remove();
    let response = await sendPostingDataViaAxios();
    if (response['success']){
        let errorDiv = $('<div class="alert alert-success error-div">Posting Schedule Updated</div>')
        $modalBody.append($errorDiv)
    }
})

//send posting day data via axios
async function sendPostingDataViaAxios(){
    console.log('starting send posting data via axios')
    const lastPostDate = $lastPostDate.val();
    const postingFrequency = $postingFrequency.val();
    const postingDay = $postingDay.val()
    const postingData = {lastPostDate: lastPostDate, postingFrequency: postingFrequency, postingDay: postingDay};
    const response = await axios.post('/api/posting', postingData)
    return response.data
}