/*jslint indent: 4 */
$(function () {
    // Set up Select2 for infodesk forms
    $("#lookup").select2({
        placeholder: "Kirjoita osa haettavaa nimeä, tai tunnisteen alkuosa.",
        minimumInputLength: 2,
        width: "30em",
        ajax: {
            url: "ta_lookup_ac",
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
    });
});
