$(document).ready(function() {

    $('#alerts-footer').find('.alert').each(function(index) {
        // Fix discrepancy between Django / Bootstrap naming conventions
        if($(this).hasClass('alert-error')) $(this).addClass('alert-danger');

        // Buffer the sending of each notification
        $(this).delay(2000 * index);

        // Hide each notification after time delay depending on the length of
        // it's message
        var time = ($(this).text().length * 30) + 1000;

        $(this).velocity('slideDown', { duration: 550 });
        $(this).velocity('fadeOut', { delay: 1200, duration: time });

    });
});
