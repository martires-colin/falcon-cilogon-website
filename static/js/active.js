$(document).ready(function() {
    $('.mr-auto .nav-item').on('click', function(e) {
        var clickedItem = $(this);
        $('.mr-auto .nav-item').each(function() {
            $(this).removeClass('active');
        });
        clickedItem.addClass('active');
        // $('.nav-link.active').removeClass('active');
        // $(this).parent('li').addClass('active');
    });
});
