(function($) {
    $(document).ready(function() {
        const $questionType = $('#id_question_type');
        const $optionInline = $('#option_set-group'); // this is the default ID Django assigns
        console.log($questionType)
        function toggleInline() {
            const type = $questionType.val();
            if (type == 'Text' || type == 'Number' || type == 'Yes/No') {
                $optionInline.hide();
                $optionInline.before('This question type does not require options.')
            } else {
                $optionInline.show();
            }
        }

        toggleInline(); // on load

        $questionType.change(function() {
            toggleInline(); // on change
        });
    });
})(django.jQuery);