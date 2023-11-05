/*jslint indent: 4 */
$(function () {
    var actionURL = $('#order-search-form').attr('action');
    // Set up Select2 for infodesk order search.
    $("#order-search").select2({
        placeholder: "Kirjoita osa haettavaa nimeä, tai tunnisteen alkuosa.",
        minimumInputLength: 2,
        width: "30em",
        ajax: {
            url: "order_search_ac",
            datatype: "json",
            data: function (term, page) {
                return {
                    term: term
                };
            },
            results: function (data, page) {
                return data;
            }
        }
    }).on('change', function(e) {
        // try to ajax-load the results page
        $('#order-search-results').empty().load(
            actionURL + '?term=' + encodeURIComponent(e.val) + ' #order-search-results');
    });
});
