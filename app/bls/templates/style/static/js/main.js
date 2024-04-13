$(document).ready(function() {
    var currentUrl = window.location.href;

    $('ul.navbar-nav li').each(function() {
        var link = $(this).find('a').attr('href');
        if (currentUrl === link) {
            $(this).addClass('active');
        }
    });
});