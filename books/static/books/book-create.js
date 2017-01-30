/**
 * Automatically submit the quick create form if user pastes in string
 * resembling an ISBN
 */
$('#id_isbn').on('paste', function() {
    setTimeout(function() {
        var input = $('#id_isbn').val();
        if (input.length == 10 || input.length == 13) {
            $('#ISBNFormSubmit').click();
        }
    }, 0);
});
