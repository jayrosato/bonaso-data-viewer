(function($) {
    $(document).ready(function() {
        const $questionType = $('#id_question_type');
        const $optionInline = $('#option_set-group'); // this is the default ID Django assigns
        const optMsg = document.createElement('p')
        optMsg.innerText = 'p'
        $optionInline.after(optMsg)

        function toggleInline() {
            const type = $questionType.val();
            if (type == 'Text' || type == 'Number' || type == 'Yes/No') {
                $optionInline.hide()
                optMsg.innerText = 'This question type does not require options.'
            } else {
                $optionInline.show();
                optMsg.innerText = ''
            }
        }
        toggleInline(); // on load

        $questionType.change(function() {
            toggleInline(); // on change
        });
    });
})(django.jQuery);