(function ($) {
    'use strict';
    $.fn.bootstrapTable.locales['fi-FI'] = {
        formatLoadingMessage: function () {
            return 'Ladataan, odota hetki...';
        },
        formatRecordsPerPage: function (pageNumber) {
            return pageNumber + ' riviä per sivu';
        },
        formatShowingRows: function (pageFrom, pageTo, totalRows) {
            return 'Näytetään sivut ' + pageFrom + ' - ' + pageTo + ' / ' + totalRows;
        },
        formatSearch: function () {
            return 'Hae';
        },
        formatNoMatches: function () {
            return 'Ei tuloksia';
        },
        formatPaginationSwitch: function () {
            return 'Piilota/Näytä sivutus';
        },
        formatRefresh: function () {
            return 'Päivitä';
        },
        formatToggle: function () {
            return 'Vaihda';
        },
        formatColumns: function () {
            return 'Sarakkeet';
        },
        formatAllRows: function () {
            return 'Kaikki';
        },
        formatExport: function () {
            return 'Vie';
        },
        formatClearFilters: function () {
            return 'Poista suodattimet';
        }
    };
    $.extend($.fn.bootstrapTable.defaults, $.fn.bootstrapTable.locales['fi-FI']);
})(jQuery);
