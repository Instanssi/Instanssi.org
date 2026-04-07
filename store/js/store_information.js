import storeInformationTemplate from "./store_information.html?minify";

/**
 * Customer info form for a store order.
 */
export const storeInformationForm = {
    template: storeInformationTemplate,
    props: {
        /** Field error messages, maps field name -> array */
        messages: Object,
        /** Store customer information */
        data: Object,
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
            this.$emit('update');
        }
    }
};

/**
 * Form group with a title, input field and any messages concerning the field.
 */
export const storeSummaryField = {
    props: {
        title: String,
        field: String,
        // type: String,
        messages: Object,
        data: Object
    },
    computed: {
        clazz() {
            let { messages, field } = this;
            if(messages && messages[field] && messages[field].length > 0) {
                return 'form-group has-error';
            }
            return 'form-group';
        },
        hasData() {
            let { data, field } = this;
            return data[field] && data[field].length > 0;
        }
    },
    template: `<div v-show="hasData" v-bind:class="clazz">
        <label class="col-sm-4 control-label">{{ title }}</label>
        <div class="col-sm-8">
            <p class="form-control-static">{{ data[field] }}</p>
            <store-messages :field="field" :messages="messages" />
        </div>
    </div>`
};

import storeSummaryTemplate from "./store_summary.html?minify";

/**
 * Immutable listing of an order's contents and customer info.
 */
export const storeOrderSummary = {
    template: storeSummaryTemplate,
    props: {
        /** Field error messages, maps field name -> array */
        messages: Object,
        /** Store customer information */
        data: Object,
        /** Shopping cart */
        cart: Array
    }
};
