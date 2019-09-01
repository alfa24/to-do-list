window.Superlists = {};
window.Superlists.initialize = function () {
    $('input[type="text"]').on('keypress', function () {
        $('.has-error').hide();
    });
};


