/*jslint indent: 4 */
$(function () {
    // Set up Select2 for infodesk forms
    $("#lookup").select2({
        placeholder: "Kirjoita osa haettavasta nimestä",
        minimumInputLength: 2,
        width: "17em",
        ajax: {
            url: "ta_lookup_ac",
            datatype: "json",
            data: function (term, page) {
                return {
                    term: term
                };
            },
            results: function (data, page) {
                var results = [];
                $.each(data, function () {
                    results.push({
                        id: this,
                        text: this
                    });
                });
                return {
                    results: results,
                    context: null,
                    more: false
                };
            }
        }
    });
});
