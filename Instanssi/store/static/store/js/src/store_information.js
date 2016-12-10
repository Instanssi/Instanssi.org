import Vue from 'vue';

Vue.component('store-information-form', {
    props: {
        /** Field error messages, maps field name -> array */
        messages: Object,
        /** Store customer information */
        data: Object
    },
    methods: {
        /**
         * Called by fields to update info, and possibly trigger live validation.
         * @param {string} fieldName - Field name/id
         * @param {Object} $event - Event object
         */
        update(fieldName, $event) {
            // could probably just use two-way binding and forget about this
            this.data[fieldName] = $event.target.value;
        }
    },
    template: require('!raw-loader!./store_information.html')
});
