(function($) {
    console.log('a')
    $(document).ready(function() {
        const $respondent = $('#resp_select');
        const $showForm = $('#resp_new');

        function toggleNewRespondent() {
            const type = $respondent.val();
            if (type == '------') {
                $showForm.hide()
            } else {
                $showForm.show();
            }
        }
        toggleNewRespondent(); // on load

        $questionType.change(function() {
            toggleNewRespondent(); // on change
        });
    });
})(django.jQuery);